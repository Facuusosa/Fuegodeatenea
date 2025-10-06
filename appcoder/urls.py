# appcoder/urls.py
from django.urls import path, include
from .views import (
    CatalogoExcelView, ExcelDetalleView,
    SahumerioCrear, SahumerioEditar, SahumerioBorrar, SahumerioDetalle
)

urlpatterns = [
    path("catalogo/", CatalogoExcelView.as_view(), name="catalogo"),
    path("sahumerios/", CatalogoExcelView.as_view(), name="sahumerios_lista"),
    path("catalogo/x/<int:idx>/", ExcelDetalleView.as_view(), name="excel_detalle"),

    path("sahumerios/<int:pk>/", SahumerioDetalle.as_view(), name="sahumerio_detalle"),
    path("sahumerios/nuevo/", SahumerioCrear.as_view(), name="sahumerio_nuevo"),
    path("sahumerios/<int:pk>/editar/", SahumerioEditar.as_view(), name="sahumerio_editar"),
    path("sahumerios/<int:pk>/borrar/", SahumerioBorrar.as_view(), name="sahumerio_borrar"),

    # ✅ carrito con namespace
    path("cart/", include(("cart.urls", "cart"), namespace="cart")),
]
