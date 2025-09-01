from django.urls import path
from .views import (
    SahumerioLista, SahumerioDetalle,
    SahumerioCrear, SahumerioEditar, SahumerioBorrar
)

urlpatterns = [
    path("sahumerios/", SahumerioLista.as_view(), name="sahumerios_lista"), 
    path("sahumerios/nuevo/", SahumerioCrear.as_view(), name="sahumerio_nuevo"),
    path("sahumerios/<int:pk>/", SahumerioDetalle.as_view(), name="sahumerio_detalle"),
    path("sahumerios/<int:pk>/editar/", SahumerioEditar.as_view(), name="sahumerio_editar"),
    path("sahumerios/<int:pk>/borrar/", SahumerioBorrar.as_view(), name="sahumerio_borrar"),
]
