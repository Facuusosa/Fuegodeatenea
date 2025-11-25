from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='detail'),
    path('add/', views.cart_add, name='add'),
    path('add/<int:product_id>/', views.cart_add_db, name='add_db'),
    path('remove/', views.cart_remove, name='remove'),
    path('clear/', views.cart_clear, name='clear'),
    path('checkout/', views.cart_checkout, name='checkout'),
    path('checkout/form/', views.cart_checkout_form, name='checkout_form'),
    path('summary/', views.cart_summary, name='summary'),
    
    # PASO 1: Nueva ruta para página de confirmación
    path('pedido-confirmado/<int:orden_id>/', views.order_success, name='order_success'),
]