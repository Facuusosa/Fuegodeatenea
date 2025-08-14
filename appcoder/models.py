from django.db import models

class Celular(models.Model):
    marca = models.CharField(max_length=60)
    modelo = models.CharField(max_length=80)
    almacenamiento_gb = models.PositiveIntegerField()
    ram_gb = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    imagen_url = models.URLField(blank=True)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.marca} {self.modelo}"
