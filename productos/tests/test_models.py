from django.test import TestCase
from django.core.exceptions import ValidationError
from productos.models import Producto


class ProductoModelTests(TestCase):
    
    def setUp(self):
        """Crear un producto base para los tests"""
        self.producto = Producto.objects.create(
            nombre="Sahumerio Lavanda",
            descripcion="Aroma relajante",
            precio=500.00,
            stock=10
        )
    
    def test_creacion_producto_basico(self):
        """Test 1: Crear un producto con campos mínimos"""
        producto = Producto.objects.create(
            nombre="Sahumerio Sándalo",
            precio=750.00
        )
        self.assertEqual(producto.nombre, "Sahumerio Sándalo")
        self.assertEqual(producto.precio, 750.00)
        self.assertEqual(producto.stock, 0)  # Default
        self.assertTrue(producto.activo)  # Default True
    
    def test_slug_se_genera_automaticamente(self):
        """Test 2: El slug se crea automáticamente del nombre"""
        producto = Producto.objects.create(
            nombre="Sahumerio Palo Santo",
            precio=600.00
        )
        self.assertEqual(producto.slug, "sahumerio-palo-santo")
    
    def test_slug_duplicado_se_incrementa(self):
        """Test 3: Si hay slug duplicado, se agrega un contador"""
        Producto.objects.create(nombre="Test", precio=100)
        producto2 = Producto.objects.create(nombre="Test", precio=200)
        
        self.assertEqual(producto2.slug, "test-1")
    
    def test_precio_negativo_no_permitido(self):
        """Test 4: No se puede guardar un precio negativo"""
        producto = Producto(
            nombre="Producto inválido",
            precio=-100.00
        )
        with self.assertRaises(ValidationError):
            producto.full_clean()
    
    def test_esta_disponible_con_stock_y_activo(self):
        """Test 5: Producto disponible si está activo y tiene stock"""
        self.producto.activo = True
        self.producto.stock = 5
        self.producto.save()
        
        self.assertTrue(self.producto.esta_disponible())
    
    def test_no_disponible_sin_stock(self):
        """Test 6: Producto no disponible si no hay stock"""
        self.producto.stock = 0
        self.producto.save()
        
        self.assertFalse(self.producto.esta_disponible())
    
    def test_no_disponible_si_inactivo(self):
        """Test 7: Producto no disponible si está marcado como inactivo"""
        self.producto.activo = False
        self.producto.save()
        
        self.assertFalse(self.producto.esta_disponible())
    
    def test_tiene_stock_suficiente(self):
        """Test 8: Verificar si hay stock para una cantidad específica"""
        self.producto.stock = 10
        self.producto.save()
        
        self.assertTrue(self.producto.tiene_stock(5))
        self.assertTrue(self.producto.tiene_stock(10))
        self.assertFalse(self.producto.tiene_stock(11))
    
    def test_reducir_stock_exitoso(self):
        """Test 9: Reducir stock cuando hay cantidad suficiente"""
        self.producto.stock = 10
        self.producto.save()
        
        resultado = self.producto.reducir_stock(3)
        self.assertTrue(resultado)
        
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 7)
    
    def test_reducir_stock_insuficiente(self):
        """Test 10: No se reduce si no hay stock suficiente"""
        self.producto.stock = 2
        self.producto.save()
        
        resultado = self.producto.reducir_stock(5)
        self.assertFalse(resultado)
        
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 2)  # No cambió
    
    def test_str_representation(self):
        """Test 11: El método __str__ retorna el nombre"""
        self.assertEqual(str(self.producto), "Sahumerio Lavanda")
    
    def test_get_precio_display(self):
        """Test 12: Formateo correcto del precio"""
        self.assertEqual(
            self.producto.get_precio_display(),
            "$500.00"
        )