from django import forms
from .models import Sahumerio

class SahumerioForm(forms.ModelForm):
    class Meta:
        model = Sahumerio
        fields = ["marca", "nombre", "descripcion", "stock", "precio", "imagen_url", "disponible"]
