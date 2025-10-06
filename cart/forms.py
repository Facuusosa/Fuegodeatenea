from django import forms

class OrderForm(forms.Form):
    MODALIDADES = [
        ("retiro", "Retiro en punto de entrega"),
        ("envio", "Envío a domicilio"),
    ]
    MEDIOS = [
        ("mercadopago", "Mercado Pago"),
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
        initial="mercadopago",
        widget=forms.Select
    )
    comentario = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Ej: horario preferido, portería, piso, depto, etc.", "rows": 3})
    )

    def clean(self):
        data = super().clean()
        if data.get("modalidad") == "envio" and not data.get("direccion"):
            self.add_error("direccion", "Ingresá la dirección completa para el envío.")
        return data