import json
from decimal import Decimal, InvalidOperation
from urllib.parse import quote
import re

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .cart import Cart
from .forms import OrderForm
from .models import Orden

# =========================
# Helpers / utilidades
# =========================

def get_product_model():
    """
    Permite usar Sahumerio (appcoder) o Producto (productos) según exista.
    """
    try:
        return apps.get_model("appcoder", "Sahumerio")
    except LookupError:
        return apps.get_model("productos", "Producto")

def _to_int(value, default=1, min_value=None, max_value=None) -> int:
    """
    Convierte a int de forma segura.
    - Aplica mínimos y máximos si se piden.
    """
    try:
        n = int(str(value).strip())
    except Exception:
        n = default
    if min_value is not None and n < min_value:
        n = min_value
    if max_value is not None and n > max_value:
        n = max_value
    return n

def _money_ar(value) -> str:
    """
    Formateo $ 12.345 (entero + separador de miles con punto).
    """
    try:
        d = Decimal(value)
    except Exception:
        d = Decimal("0")
    i = int(d)
    return "$ " + format(i, ",").replace(",", ".")

def _parse_price_ar(raw: str) -> Decimal:
    """
    Acepta 1.234,56  o  1234.56  y devuelve Decimal. Vacío -> 0.
    """
    if raw is None:
        return Decimal("0")
    s = str(raw).strip()
    if not s:
        return Decimal("0")
    s = s.replace(".", "").replace(",", ".")
    try:
        return Decimal(s)
    except (InvalidOperation, TypeError):
        return Decimal("0")

def _cart_total(cart: Cart) -> Decimal:
    try:
        return Decimal(cart.total)
    except Exception:
        try:
            return Decimal(cart.get_total_price())
        except Exception:
            total = Decimal("0")
            for it in cart:
                total += Decimal(it.get("subtotal", 0))
            return total

def _build_wa_message(cart: Cart, data: dict | None = None) -> str:
    """
    PASO 2 - Arma el texto para WhatsApp con items + datos del cliente.
    VERSIÓN MEJORADA: Formato más claro, separadores visuales, emojis contextuales.
    """
    lines = []
    
    # Header con diseño
    lines.append("╔═══════════════════════════╗")
    
    # Si hay data (orden confirmada), mostrar número de orden
    if data and 'orden_id' in data:
        lines.append(f"   🛒 *NUEVO PEDIDO #{data['orden_id']}*")
    else:
        lines.append("   🛒 *NUEVO PEDIDO*")
    
    lines.append("╚═══════════════════════════╝")
    lines.append("")
    
    # Sección de productos
    lines.append("📦 *PRODUCTOS*")
    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    
    for it in cart:
        q = int(it.get("quantity", 1))
        name = str(it.get("name") or "Producto")
        price = _money_ar(it.get("price", 0))
        subtotal = _money_ar(it.get("subtotal", 0))
        
        lines.append(f"• *{q}x* {name}")
        lines.append(f"  💰 {price} c/u → *{subtotal}*")
        lines.append("")
    
    lines.append("━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"💵 *TOTAL: {_money_ar(_cart_total(cart))}*")
    lines.append("")

    # Si hay datos del cliente, mostrarlos
    if data is not None:
        lines.append("👤 *DATOS DEL CLIENTE*")
        lines.append("━━━━━━━━━━━━━━━━━━━━━")
        
        nombre = data.get("nombre") or ""
        tel = data.get("telefono") or ""
        email = data.get("email") or ""
        modalidad = (data.get("modalidad") or "retiro").lower()
        direccion = data.get("direccion") or ""
        medio_pago_value = data.get("medio_pago")
        medio_pago_label = dict(OrderForm.MEDIOS).get(medio_pago_value, medio_pago_value or "")
        comentario = data.get("comentario") or ""

        if nombre:
            lines.append(f"*Nombre:* {nombre}")
        
        if tel:
            # Formatear teléfono con espacios para mejor lectura
            tel_formatted = tel
            if len(tel) == 10 and tel.isdigit():
                # Formato: 11 3456-7890
                tel_formatted = f"{tel[:2]} {tel[2:6]}-{tel[6:]}"
            lines.append(f"📞 *Teléfono:* {tel_formatted}")
        
        if email:
            lines.append(f"📧 *Email:* {email}")
        
        # Modalidad con emoji específico
        if modalidad == "envio":
            lines.append(f"📍 *Modalidad:* Envío a domicilio 🚚")
            if direccion:
                lines.append(f"🏠 *Dirección:* {direccion}")
        else:
            lines.append(f"📍 *Modalidad:* Retiro en punto de entrega 📦")
        
        # Medio de pago con emoji
        if medio_pago_value == "mp":
            emoji = "💳"
        elif medio_pago_value == "transferencia":
            emoji = "🏦"
        else:
            emoji = "💵"
        
        if medio_pago_label:
            lines.append(f"{emoji} *Pago:* {medio_pago_label}")
        
        # Comentario si existe
        if comentario:
            lines.append("")
            lines.append(f"📝 *Comentario:* {comentario}")
        
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━")

    # Footer con call to action
    lines.append("")
    if data:
        lines.append("¿Confirmamos el pedido? ✅")
    else:
        lines.append("¿Te interesa? ¡Hablemos! 💬")

    return "\n".join(lines)

def _redirect_back(request: HttpRequest, fallback_name="cart:detail") -> HttpResponse:
    """
    Intenta volver a la página anterior; si no, al detalle del carrito.
    """
    ref = request.META.get("HTTP_REFERER")
    return redirect(ref) if ref else redirect(fallback_name)

def format_argentina_whatsapp(phone_raw):
    """
    Convierte cualquier número argentino a formato WhatsApp internacional:
    Siempre 549[código área][celular sin 15]
    Ej: '01112345678', '1134567890', '15 3456-7890' => '54911xxxxxxx'
    """
    num = re.sub(r"\D", "", phone_raw or "")
    # Eliminar '0' inicial si existe
    if num.startswith("0"):
        num = num[1:]
    # Eliminar '15' si lo tiene pos-código de área
    if len(num) == 10 and num[2:4] == "15":
        num = num[:2] + num[4:]
    elif len(num) == 11 and num[3:5] == "15":
        num = num[:3] + num[5:]
    # Añadir el '9' de WhatsApp si no está
    if not num.startswith("9"):
        num = "9" + num
    return f"54{num}"

# =========================
# Vistas
# =========================

def cart_detail(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})

@csrf_exempt
@require_POST
def cart_add(request: HttpRequest) -> HttpResponse:
    """
    BUG #4 CORREGIDO: Permite quantity=0 para eliminar productos.
    Agrega o reemplaza cantidad (según 'replace'=1) para items de DB o XLS.
    """
    cart = Cart(request)
    origin = (request.POST.get("origin") or "X").upper()
    replace = str(request.POST.get("replace", "0")) == "1"
    quantity_raw = request.POST.get("quantity", "1")

    # BUG #4 CORREGIDO: min_value=0 para permitir eliminación
    quantity = _to_int(quantity_raw, default=1, min_value=0)

    if origin == "DB":
        Product = get_product_model()
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        product_name = getattr(product, 'nombre', str(product))
        
        # BUG #4 CORREGIDO: Eliminar explícitamente si qty <= 0
        if quantity <= 0:
            cart.remove(product_id)
            messages.error(request, f"Quitaste {product_name} del carrito.")
            return _redirect_back(request)
        
        old_qty = 0
        for item in cart:
            if str(item.get("id")) == str(product_id):
                old_qty = int(item.get("quantity", 0))
                break
        
        cart.add(product=product, quantity=quantity, replace_quantity=replace)
        
        if quantity > old_qty:
            messages.success(request, f"Agregaste {product_name} al carrito.")
        elif quantity < old_qty:
            messages.info(request, f"Restaste una unidad de {product_name}.")
        else:
            messages.info(request, f"Cantidad sin cambios.")
        
        return _redirect_back(request)

    # XLS / payload
    product_id = request.POST.get("product_id")
    name = (request.POST.get("name") or "").strip()
    price = _parse_price_ar(request.POST.get("price", "0"))
    img = (request.POST.get("img") or "").strip()
    display_name = name or "producto"
    
    # BUG #4 CORREGIDO: Eliminar explícitamente si qty <= 0
    if quantity <= 0:
        cart.remove(product_id)
        messages.error(request, f"Quitaste {display_name} del carrito.")
        return _redirect_back(request)

    old_qty = 0
    for item in cart:
        if str(item.get("id")) == str(product_id):
            old_qty = int(item.get("quantity", 0))
            break

    cart.add_payload(
        product_id=product_id,
        name=name,
        price=price,
        img=img,
        quantity=quantity,
        replace_quantity=replace,
    )
    
    if quantity > old_qty:
        messages.success(request, f"Agregaste {display_name} al carrito.")
    elif quantity < old_qty:
        messages.info(request, f"Restaste una unidad de {display_name}.")
    else:
        messages.info(request, f"Cantidad sin cambios.")
    
    return _redirect_back(request)

@csrf_exempt
@require_POST
def cart_add_db(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Variante específica para agregar desde ruta con pk en la URL.
    """
    cart = Cart(request)
    Product = get_product_model()
    product = get_object_or_404(Product, id=product_id)

    quantity = _to_int(request.POST.get("quantity", "1"), default=1, min_value=1)
    replace = str(request.POST.get("replace", "0")) == "1"

    cart.add(product=product, quantity=quantity, replace_quantity=replace)
    product_name = getattr(product, 'nombre', str(product))
    messages.success(request, f"Agregaste {product_name} al carrito.")
    return _redirect_back(request)

@csrf_exempt
@require_POST
def cart_remove(request: HttpRequest) -> HttpResponse:
    """
    Elimina un ítem del carrito (botón 'Quitar').
    """
    cart = Cart(request)
    product_id = request.POST.get("product_id")
    if product_id is not None:
        cart.remove(product_id)
        messages.error(request, "Quitaste un producto del carrito.")
    return _redirect_back(request)

@csrf_exempt
@require_POST
def cart_clear(request: HttpRequest) -> HttpResponse:
    """
    Vacía todo el carrito (botón 'Vaciar carrito').
    """
    cart = Cart(request)
    cart.clear()
    messages.warning(request, "Vaciaste el carrito.")
    return _redirect_back(request)

def cart_checkout(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")
    msg = _build_wa_message(cart)
    phone_raw = (getattr(settings, "WHATSAPP_PHONE", "") or "").strip()
    phone = format_argentina_whatsapp(phone_raw)
    wa_url = f"https://wa.me/{phone}?text={quote(msg)}" if phone else f"https://wa.me/?text={quote(msg)}"
    return redirect(wa_url)

def cart_checkout_form(request: HttpRequest) -> HttpResponse:
    """
    PASO 1 - Procesa el formulario de checkout:
    1. Guarda la orden en BD
    2. Limpia el carrito
    3. Redirige a página de confirmación (con botón WhatsApp mejorado)
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # Guardar orden en BD
            orden = Orden.objects.create(
                nombre=form.cleaned_data.get('nombre', ''),
                telefono=form.cleaned_data.get('telefono', ''),
                email=form.cleaned_data.get('email', ''),
                modalidad=form.cleaned_data.get('modalidad', 'retiro'),
                direccion=form.cleaned_data.get('direccion', ''),
                medio_pago=form.cleaned_data.get('medio_pago', 'mp'),
                comentario=form.cleaned_data.get('comentario', ''),
                total=_cart_total(cart),
                items_json=json.dumps(list(cart)),
                estado='pendiente',
            )
            
            # Limpiar carrito
            cart.clear()
            
            # Mensaje de éxito
            messages.success(
                request, 
                f"¡Orden #{orden.id} creada exitosamente!"
            )
            
            # PASO 1: Redirigir a página de confirmación en vez de WhatsApp directo
            return redirect('cart:order_success', orden_id=orden.id)
    else:
        form = OrderForm()

    return render(request, "cart/checkout_form.html", {"cart": cart, "form": form})

def cart_summary(request: HttpRequest) -> JsonResponse:
    """
    Vista API para obtener resumen del carrito (usada por AJAX)
    """
    cart = Cart(request)
    cart_items = list(cart)
    
    summary = {
        'total_items': len(cart),
        'total_price': str(_cart_total(cart)),
        'items': []
    }
    
    for item in cart_items[:5]:
        summary['items'].append({
            'name': item.get('name', 'Producto'),
            'quantity': item.get('quantity', 1),
            'price': str(item.get('price', 0)),
            'subtotal': str(item.get('subtotal', 0)),
            'image_url': item.get('image_url', ''),
        })
    
    return JsonResponse(summary)

# =========================
# PASO 1 - Nueva vista
# =========================

def order_success(request: HttpRequest, orden_id: int) -> HttpResponse:
    """
    PASO 1 - Página de confirmación después de crear una orden.
    Muestra resumen del pedido y botón para WhatsApp con mensaje mejorado.
    """
    orden = get_object_or_404(Orden, id=orden_id)
    
    # Parsear items del JSON
    try:
        items = json.loads(orden.items_json)
    except:
        items = []
    
    # Generar URL de WhatsApp con mensaje mejorado (PASO 2)
    cart_temp = type('obj', (object,), {
        '__iter__': lambda self: iter(items),
        'total': float(orden.total)
    })()
    
    # PASO 2: Agregar orden_id al dict para que aparezca en el mensaje
    msg = _build_wa_message(cart_temp, {
        'orden_id': orden.id,
        'nombre': orden.nombre,
        'telefono': orden.telefono,
        'email': orden.email,
        'modalidad': orden.modalidad,
        'direccion': orden.direccion,
        'medio_pago': orden.medio_pago,
        'comentario': orden.comentario,
    })
    
    phone_raw = (getattr(settings, "WHATSAPP_PHONE", "") or "").strip()
    phone = format_argentina_whatsapp(phone_raw)
    whatsapp_url = f"https://wa.me/{phone}?text={quote(msg)}" if phone else f"https://wa.me/?text={quote(msg)}"
    
    context = {
        'orden': orden,
        'items': items,
        'whatsapp_url': whatsapp_url,
    }
    
    return render(request, "cart/order_success.html", context)