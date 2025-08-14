from django.contrib import admin
from django.urls import path
from appcoder import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.celulares_lista, name='home'),
    path('celulares/', views.celulares_lista, name='celulares'),
    path('celulares/nuevo/', views.celular_nuevo, name='celular_nuevo'),
]
