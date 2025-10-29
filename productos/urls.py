from django.urls import path
from .views import catalogo

urlpatterns = [
    path('catalogo/', catalogo, name='catalogo'),
]

from .views import test_imagen_url

urlpatterns += [
    path('test-imagen/', test_imagen_url),
]
