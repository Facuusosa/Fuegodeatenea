from django.db import models

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.nombre

class Sahumerio(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name="sahumerios")
    nombre = models.CharField(max_length=120)
    descripcion = models.CharField(max_length=200, blank=True, default="")  # 👈 acá
    stock = models.PositiveIntegerField(default=0)
    precio = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    imagen_url = models.URLField(blank=True)
    disponible = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.nombre} ({self.marca})"
