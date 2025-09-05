from django.contrib import admin
from .models import Sahumerio

@admin.register(Sahumerio)
class SahumerioAdmin(admin.ModelAdmin):
    list_display = ("marca", "nombre", "precio", "stock", "activo", "actualizado")
    list_filter = ("activo",)
    search_fields = ("marca", "nombre", "descripcion")
