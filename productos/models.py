from django.db import models
from cloudinary.models import CloudinaryField

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = CloudinaryField('imagen', blank=True, null=True)  # Este es el campo correcto

    def __str__(self):
        return self.nombre
