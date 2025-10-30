from decimal import Decimal, InvalidOperation
from urllib.parse import quote

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .cart import Cart
from .forms import OrderForm


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
    Arma el texto para WhatsApp con items + (opcional) datos del cliente.
    """
    lines = []
    lines.append("🛒 *Nuevo pedido*")
    lines.append("")
    for it in cart:
        q = int(it.get("quantity", 1))
        name = str(it.get("name") or "Producto")
        price = _money_ar(it.get("price", 0))
        subtotal = _money_ar(it.get("subtotal", 0))
        lines.append(f"- {q} × {name} — {price} = {subtotal}")
    lines.append("")
    lines.append(f"Total: {_money_ar(_cart_total(cart))}")

    if data is not None:
        lines.append("")
        lines.append("👤 *Datos del cliente*")
        nombre = data.get("nombre") or ""
        tel = data.get("telefono") or ""
        modalidad = (data.get("modalidad") or "retiro").lower()
        direccion = data.get("direccion") or ""
        medio_pago_value = data.get("medio_pago")
        medio_pago_label = dict(OrderForm.MEDIOS).get(medio_pago_value, medio_pago_value or "")
        comentario = data.get("comentario") or ""

        if nombre:
            lines.append(f"• Nombre: {nombre}")
        if tel:
            lines.append(f"• Teléfono: {tel}")
        if modalidad == "envio":
            lines.append("• Modalidad: Envío a domicilio")
            if direccion:
                lines.append(f"• Dirección: {direccion}")
        else:
            lines.append("• Modalidad: Retiro en punto de entrega")
        if medio_pago_label:
            lines.append(f"• Medio de pago: {medio_pago_label}")
        if comentario:
            lines.append(f"• Comentario: {comentario}")

    lines.append("")
    lines.append("¿Podemos coordinar entrega/pago? 🙌")
    return "\n".join(lines)


def _redirect_back(request: HttpRequest, fallback_name="cart:detail") -> HttpResponse:
    """
    Intenta volver a la página anterior; si no, al detalle del carrito.
    """
    ref = request.META.get("HTTP_REFERER")
    return redirect(ref) if ref else redirect(fallback_name)


# =========================
# Vistas
# =========================


def cart_detail(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


@csrf_protect
@require_POST
def cart_add(request: HttpRequest) -> HttpResponse:
    """
    Agrega o reemplaza cantidad (según 'replace'=1) para items de DB o XLS.
    - quantity se normaliza a mínimo 1 para evitar eliminar vía '−'.
    - Muestra mensajes contextuales según si se agregó, restó o mantuvo.
    """
    cart = Cart(request)
    origin = (request.POST.get("origin") or "X").upper()
    replace = str(request.POST.get("replace", "0")) == "1"
    quantity_raw = request.POST.get("quantity", "1")

    quantity = _to_int(quantity_raw, default=1, min_value=1)

    if origin == "DB":
        Product = get_product_model()
        product_id = request.POST.get("product_id")
        product = get_object_or_404(Product, id=product_id)
        
        # Obtener cantidad anterior
        old_qty = 0
        for item in cart:
            if str(item.get("id")) == str(product_id):
                old_qty = int(item.get("quantity", 0))
                break
        
        cart.add(product=product, quantity=quantity, replace_quantity=replace)
        
        # Mensaje contextual
        product_name = getattr(product, 'nombre', str(product))
        if quantity > old_qty:
            messages.success(request, f"Agregaste {product_name} al carrito.")
        elif quantity < old_qty:
            messages.info(request, f"Restaste una unidad del carrito de {product_name}.")
        else:
            messages.info(request, f"Cantidad sin cambios.")
        
        return _redirect_back(request)

    # XLS / payload
    product_id = request.POST.get("product_id")
    name = (request.POST.get("name") or "").strip()
    price = _parse_price_ar(request.POST.get("price", "0"))
    img = (request.POST.get("img") or "").strip()

    # Obtener cantidad anterior
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
    
    # Mensaje contextual
    display_name = name or "producto"
    if quantity > old_qty:
        messages.success(request, f"Agregaste {display_name} al carrito.")
    elif quantity < old_qty:
        messages.info(request, f"Restaste una unidad del carrito de {display_name}.")
    else:
        messages.info(request, f"Cantidad sin cambios.")
    
    return _redirect_back(request)


@csrf_protect
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


@csrf_protect
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


@csrf_protect
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
    phone = (getattr(settings, "WHATSAPP_PHONE", "") or "").strip()
    wa_url = f"https://wa.me/{phone}?text={quote(msg)}" if phone else f"https://wa.me/?text={quote(msg)}"
    return redirect(wa_url)


def cart_checkout_form(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            msg = _build_wa_message(cart, form.cleaned_data)
            phone = (getattr(settings, "WHATSAPP_PHONE", "") or "").strip()
            wa_url = f"https://wa.me/{phone}?text={quote(msg)}" if phone else f"https://wa.me/?text={quote(msg)}"
            return redirect(wa_url)
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
