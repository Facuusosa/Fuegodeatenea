from django.db import models
from django.utils import timezone
from decimal import Decimal


class Orden(models.Model):
    """
    Registro de cada compra: quién, qué, cuándo, cómo.
    """
    # Datos del cliente
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    
    # Modalidad de entrega
    MODALIDAD_CHOICES = [
        ('retiro', 'Retiro en punto de entrega'),
        ('envio', 'Envío a domicilio'),
    ]
    modalidad = models.CharField(max_length=10, choices=MODALIDAD_CHOICES, default='retiro')
    direccion = models.TextField(blank=True, null=True)
    
    # Método de pago
    # NOTA: Estos valores (mp, efectivo, transferencia) son los CORRECTOS
    # y fueron usados como referencia para corregir forms.py
    MEDIOS_CHOICES = [
        ('mp', 'Mercado Pago'),
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
    ]
    medio_pago = models.CharField(max_length=20, choices=MEDIOS_CHOICES, default='mp')
    
    # Comentarios
    comentario = models.TextField(blank=True, null=True)
    
    # Montos
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    # Estado (para después)
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # JSON con items (simple pero funciona)
    items_json = models.TextField(default='[]')
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"
    
    def __str__(self):
        return f"Orden #{self.id} - {self.nombre} - ${self.total}"