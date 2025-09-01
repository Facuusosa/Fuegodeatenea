from django.contrib import admin
from .models import Marca, Sahumerio

@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)

@admin.register(Sahumerio)
class SahumerioAdmin(admin.ModelAdmin):
    list_display = ("marca", "nombre", "stock", "precio", "disponible")
    search_fields = ("nombre", "marca__nombre")
    list_filter = ("marca", "disponible")
