from django.db import models

class Sahumerio(models.Model):
    marca = models.CharField(max_length=80, blank=True, default='')
    nombre = models.CharField(max_length=120)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True)
    imagen_url = models.URLField(blank=True)
    imagen_file = models.ImageField(upload_to='productos/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['marca', 'nombre']

    def __str__(self):
        return f'{self.marca} {self.nombre}'

    def imagen_resuelta(self):
        if self.imagen_file:
            return self.imagen_file.url
        return self.imagen_url or ''
