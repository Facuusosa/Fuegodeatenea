from django.contrib import admin
from .models import Celular

@admin.register(Celular)
class CelularAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'almacenamiento_gb', 'ram_gb', 'precio', 'disponible')
    search_fields = ('marca', 'modelo')
    list_filter = ('marca', 'disponible')
