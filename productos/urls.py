from django.urls import path
from .views import catalogo_view

app_name = 'productos'

urlpatterns = [
    path('sahumerios/', catalogo_view, name='catalogo'),
    # Agrega aquí otras URLs de productos según necesites
    # path('sahumerios/<int:id>/', producto_detalle_view, name='sahumerio_detalle'),
    # path('categoria/<str:categoria>/', productos_por_categoria, name='productos_categoria'),
]