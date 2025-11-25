from django.contrib import admin
from .models import Orden
import json

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    # Qué columnas se ven en la lista principal
    list_display = ['id', 'nombre', 'telefono', 'total', 'modalidad', 'medio_pago', 'estado', 'fecha_creacion']
    
    # Filtros en la barra lateral
    list_filter = ['estado', 'modalidad', 'medio_pago', 'fecha_creacion']
    
    # Buscador
    search_fields = ['nombre', 'telefono', 'email']
    
    # Poder editar el estado directamente desde la lista
    list_editable = ['estado']
    
    # Ordenar por más reciente primero
    ordering = ['-fecha_creacion']
    
    # Campos de solo lectura
    readonly_fields = ['fecha_creacion', 'actualizado', 'ver_items']
    
    # Cómo se agrupan los campos
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('nombre', 'telefono', 'email')
        }),
        ('Entrega', {
            'fields': ('modalidad', 'direccion')
        }),
        ('Pago', {
            'fields': ('medio_pago', 'total')
        }),
        ('Productos', {
            'fields': ('ver_items',)
        }),
        ('Comentarios', {
            'fields': ('comentario',)
        }),
        ('Estado y Fechas', {
            'fields': ('estado', 'fecha_creacion', 'actualizado')
        }),
    )
    
    # Función para ver los items de forma linda
    def ver_items(self, obj):
        try:
            items = json.loads(obj.items_json)
            html = "<ul>"
            for item in items:
                nombre = item.get('name', 'Producto')
                cantidad = item.get('quantity', 0)
                precio = item.get('price', 0)
                subtotal = item.get('subtotal', 0)
                html += f"<li><strong>{cantidad}x</strong> {nombre} - ${precio} = <strong>${subtotal}</strong></li>"
            html += "</ul>"
            return html
        except:
            return "Error al cargar items"
    
    ver_items.short_description = "Productos del pedido"
    ver_items.allow_tags = True