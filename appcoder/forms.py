from django import forms
from .models import Sahumerio

class SahumerioForm(forms.ModelForm):
    class Meta:
        model = Sahumerio
        fields = ['marca', 'nombre', 'precio', 'stock', 'descripcion', 'imagen_url', 'imagen_file', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3})
        }
