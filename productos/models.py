from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from django.utils import timezone
from cloudinary.models import CloudinaryField


class Producto(models.Model):
    """
    Modelo de Producto con todos los campos necesarios.
    ✅ Versión segura que permite migraciones sin errores.
    """
    # Campos que YA EXISTEN en la DB
    nombre = models.CharField(
        max_length=100,
        help_text="Nombre del sahumerio"
    )
    
    descripcion = models.TextField(
        blank=True,
        help_text="Descripción detallada del producto"
    )
    
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Precio en pesos argentinos"
    )
    
    imagen = CloudinaryField(
        'imagen',
        blank=True,
        null=True,
        help_text="Imagen del producto"
    )
    
    # ✅ CAMPOS NUEVOS (con valores por defecto seguros)
    slug = models.SlugField(
        max_length=120,
        blank=True,
        null=True,  # Permite NULL para migración
        unique=False,  # Sin unique por ahora
        help_text="Se genera automáticamente del nombre"
    )
    
    categoria = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Categoría del producto"
    )
    
    marca = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Marca del producto"
    )
    
    stock = models.PositiveIntegerField(
        default=10,  # Por defecto tienen stock
        help_text="Cantidad disponible"
    )
    
    activo = models.BooleanField(
        default=True,
        help_text="Producto visible en catálogo"
    )
    
    creado = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha de creación"
    )
    
    modificado = models.DateTimeField(
        default=timezone.now,
        help_text="Última modificación"
    )
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-creado']
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        """Genera el slug y actualiza fecha de modificación"""
        # Generar slug si no existe
        if not self.slug and self.nombre:
            base_slug = slugify(self.nombre)
            slug = base_slug
            counter = 1
            while Producto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Actualizar fecha de modificación
        if self.pk:
            self.modificado = timezone.now()
        
        super().save(*args, **kwargs)
    
    def esta_disponible(self):
        """Verifica si está disponible para venta"""
        return self.activo and self.stock > 0
    
    def get_precio_display(self):
        """Retorna el precio formateado"""
        return f"${self.precio:,.2f}"