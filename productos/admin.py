from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Configuración del admin para Producto.
    ✅ Incluye filtros por marca y categoría
    """
    list_display = [
        'nombre',
        'marca',
        'categoria',
        'precio',
        'stock',
        'activo',
        'creado'
    ]
    
    list_filter = [
        'activo',
        'marca',
        'categoria',
        'creado'
    ]
    
    search_fields = [
        'nombre',
        'descripcion',
        'marca',
        'categoria'
    ]
    
    list_editable = [
        'precio',
        'stock',
        'activo'
    ]
    
    readonly_fields = [
        'slug',
        'creado',
        'modificado'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'slug', 'descripcion')
        }),
        ('Clasificación', {
            'fields': ('marca', 'categoria')
        }),
        ('Precio y Stock', {
            'fields': ('precio', 'stock')
        }),
        ('Imagen', {
            'fields': ('imagen',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Fechas', {
            'fields': ('creado', 'modificado'),
            'classes': ('collapse',)
        }),
    )
    
    # Acciones personalizadas
    actions = ['activar_productos', 'desactivar_productos', 'agotar_stock']
    
    def activar_productos(self, request, queryset):
        """Activa los productos seleccionados"""
        updated = queryset.update(activo=True)
        self.message_user(request, f'{updated} producto(s) activado(s).')
    activar_productos.short_description = "Activar productos seleccionados"
    
    def desactivar_productos(self, request, queryset):
        """Desactiva los productos seleccionados"""
        updated = queryset.update(activo=False)
        self.message_user(request, f'{updated} producto(s) desactivado(s).')
    desactivar_productos.short_description = "Desactivar productos seleccionados"
    
    def agotar_stock(self, request, queryset):
        """Pone el stock en 0 para los productos seleccionados"""
        updated = queryset.update(stock=0)
        self.message_user(request, f'Stock agotado para {updated} producto(s).')
    agotar_stock.short_description = "Agotar stock de productos seleccionados"