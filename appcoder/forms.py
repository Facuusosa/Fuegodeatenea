from django import forms
from .models import Celular

class CelularForm(forms.ModelForm):
    class Meta:
        model = Celular
        fields = ['marca', 'modelo', 'almacenamiento_gb', 'ram_gb', 'precio', 'imagen_url', 'disponible']
