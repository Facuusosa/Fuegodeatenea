from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from productos.models import Producto


def catalogo_view(request):
    """
    Vista del catálogo con filtros completos y funcionales.
    ✅ VERSIÓN CORREGIDA - Muestra todos los productos
    """
    # Query base: solo productos activos (SIN filtrar por stock aquí)
    productos = Producto.objects.filter(activo=True)
    
    # ========== APLICAR FILTROS ==========
    
    # 1. Búsqueda por texto
    search = request.GET.get('search', '').strip()
    if search:
        productos = productos.filter(
            Q(nombre__icontains=search) | 
            Q(descripcion__icontains=search) |
            Q(marca__icontains=search) |
            Q(categoria__icontains=search)
        )
    
    # 2. Filtro por categoría
    categoria = request.GET.get('categoria', '').strip()
    if categoria:
        productos = productos.filter(categoria__iexact=categoria)
    
    # 3. Filtro por marca
    marca = request.GET.get('marca', '').strip()
    if marca:
        productos = productos.filter(marca__iexact=marca)
    
    # 4. Filtro por precio mínimo
    precio_min = request.GET.get('precio_min', '').strip()
    if precio_min:
        try:
            productos = productos.filter(precio__gte=float(precio_min))
        except (ValueError, TypeError):
            pass
    
    # 5. Filtro por precio máximo
    precio_max = request.GET.get('precio_max', '').strip()
    if precio_max:
        try:
            productos = productos.filter(precio__lte=float(precio_max))
        except (ValueError, TypeError):
            pass
    
    # 6. Filtro por disponibilidad
    disponible = request.GET.get('disponible', '')
    if disponible == 'si':
        productos = productos.filter(stock__gt=0)
    elif disponible == 'no':
        productos = productos.filter(stock=0)
    # Si disponible está vacío, muestra TODOS (con y sin stock)
    
    # 7. Ordenamiento
    orden = request.GET.get('orden', 'nuevo')
    orden_map = {
        'nuevo': '-creado',
        'antiguo': 'creado',
        'precio_asc': 'precio',
        'precio_desc': '-precio',
        'nombre_asc': 'nombre',
        'nombre_desc': '-nombre',
    }
    productos = productos.order_by(orden_map.get(orden, '-creado'))
    
    # ========== OBTENER VALORES ÚNICOS PARA SELECTORES ==========
    # Ahora incluye productos con y sin stock
    
    todas_categorias = (
        Producto.objects
        .filter(activo=True, categoria__isnull=False)
        .exclude(categoria='')
        .values_list('categoria', flat=True)
        .distinct()
        .order_by('categoria')
    )
    
    todas_marcas = (
        Producto.objects
        .filter(activo=True, marca__isnull=False)
        .exclude(marca='')
        .values_list('marca', flat=True)
        .distinct()
        .order_by('marca')
    )
    
    # ========== PREPARAR FILTROS ACTIVOS ==========
    
    filtros_activos = []
    if search:
        filtros_activos.append(('Búsqueda', search))
    if categoria:
        filtros_activos.append(('Categoría', categoria))
    if marca:
        filtros_activos.append(('Marca', marca))
    if precio_min:
        filtros_activos.append(('Precio mín', f'${precio_min}'))
    if precio_max:
        filtros_activos.append(('Precio máx', f'${precio_max}'))
    if disponible:
        texto_disponible = 'En stock' if disponible == 'si' else 'Sin stock'
        filtros_activos.append(('Disponibilidad', texto_disponible))
    
    # ========== PAGINACIÓN ==========
    
    paginator = Paginator(productos, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # ========== CONTEXTO ==========
    
    context = {
        'productos': page_obj,
        'total_productos': paginator.count,
        'todas_categorias': todas_categorias,
        'todas_marcas': todas_marcas,
        'filtros_activos': filtros_activos,
        'search': search,
        'categoria': categoria,
        'marca': marca,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'disponible': disponible,
        'orden': orden,
    }
    
    return render(request, 'catalogo.html', context)