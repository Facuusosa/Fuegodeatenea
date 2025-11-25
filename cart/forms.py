import re
from django import forms


class OrderForm(forms.Form):
    MODALIDADES = [
        ("retiro", "Retiro en punto de entrega"),
        ("envio", "Envío a domicilio"),
    ]
    # BUG #1 CORREGIDO: Valores unificados con models.py (mp, efectivo, transferencia)
    MEDIOS = [
        ("mp", "Mercado Pago"),
        ("transferencia", "Transferencia"),
        ("efectivo", "Efectivo"),
    ]

    nombre = forms.CharField(
        max_length=120,
        widget=forms.TextInput(attrs={"placeholder": "Ingresá tu nombre completo"})
    )
    telefono = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "Ej: 11 1234-5678"})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "tucorreo@ejemplo.com (opcional)"})
    )
    modalidad = forms.ChoiceField(
        choices=MODALIDADES,
        widget=forms.RadioSelect
    )
    direccion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Calle, número, localidad"})
    )
    medio_pago = forms.ChoiceField(
        choices=MEDIOS,
        initial="mp",  # BUG #1 CORREGIDO: Cambiado de "mercadopago" a "mp"
        widget=forms.Select
    )
    comentario = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Ej: horario preferido, portería, piso, depto, etc.", "rows": 3})
    )

    def clean_telefono(self):
        """
        BUG #2 CORREGIDO: Valida y limpia números de teléfono argentinos.
        Acepta formatos: 1134567890, 011 1234-5678, +54 9 11 3456-7890, 15-3456-7890
        """
        telefono_raw = self.cleaned_data.get('telefono', '').strip()
        
        # Remover todos los caracteres no numéricos
        telefono_limpio = re.sub(r'\D', '', telefono_raw)
        
        # Validar longitud (números argentinos tienen entre 8 y 13 dígitos)
        if len(telefono_limpio) < 8 or len(telefono_limpio) > 13:
            raise forms.ValidationError(
                "Ingresá un teléfono válido (Ej: 11 1234-5678)"
            )
        
        # Retornar el teléfono limpio (solo dígitos)
        return telefono_limpio

    def clean(self):
        data = super().clean()
        if data.get("modalidad") == "envio" and not data.get("direccion"):
            self.add_error("direccion", "Ingresá la dirección completa para el envío.")
        return data