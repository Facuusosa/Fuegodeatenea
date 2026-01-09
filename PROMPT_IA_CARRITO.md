# Prompt para resolver problema de carrito de compras

## Contexto del proyecto

Tengo una aplicación Django con un catálogo de productos (sahumerios) que permite agregar productos al carrito. El catálogo muestra productos desde una base de datos y desde un archivo Excel.

## Problema específico

**Síntoma principal**: Los botones de cantidad (+ y -) y el botón "Agregar al carrito" no funcionan correctamente en algunos productos del catálogo. Algunos productos funcionan bien, pero otros no responden al hacer clic.

**Comportamiento esperado**:
1. El usuario hace clic en el botón "+" para aumentar la cantidad (ej: de 1 a 5)
2. El usuario hace clic en "🛒 Agregar al carrito"
3. Se agregan 5 unidades del producto al carrito

**Comportamiento actual**:
- En algunos productos, los botones "+" y "-" no responden
- En algunos productos, el botón "Agregar al carrito" no funciona
- No hay errores visibles en la consola del navegador
- El problema es inconsistente: algunos productos funcionan, otros no

## Estructura del código actual

### HTML (template catalogo.html)
```html
<!-- Selector de cantidad -->
<div class="quantity-selector" data-product-id="...">
  <button type="button" class="quantity-btn decrease-btn">−</button>
  <input type="number" class="quantity-input" value="1" min="1" max="{{ item.stock }}" readonly>
  <button type="button" class="quantity-btn increase-btn">+</button>
</div>

<!-- Formulario para agregar al carrito -->
<form method="post" action="{% url 'cart:add' %}" class="add-to-cart-form">
  {% csrf_token %}
  <input type="hidden" name="origin" value="DB o XLS">
  <input type="hidden" name="product_id" value="...">
  <input type="hidden" name="quantity" value="1" class="qty-hidden">
  <button type="submit" class="btn-add-cart">🛒 Agregar al carrito</button>
</form>
```

### JavaScript actual
El código JavaScript:
- Usa una función auto-ejecutada (IIFE) para evitar conflictos
- Inicializa los event listeners en `DOMContentLoaded`
- Tiene funciones `syncQuantity()` y `addToCart()`
- Usa `addEventListener` para los botones de cantidad
- Usa `fetch()` con AJAX para agregar al carrito

### Backend (Django)
- Endpoint: `cart:add` que acepta POST
- Parámetros: `origin`, `product_id`, `quantity`, etc.
- Retorna JSON con `success`, `message`, `cart_total`

## Lo que se ha intentado

1. ✅ Simplificar el código JavaScript eliminando listeners duplicados
2. ✅ Usar `addEventListener` en lugar de `onclick`
3. ✅ Agregar `stopPropagation()` y `stopImmediatePropagation()`
4. ✅ Sincronizar la cantidad antes de enviar el formulario
5. ✅ Forzar la cantidad en el FormData
6. ✅ Agregar validaciones para elementos que no existen
7. ✅ Manejar casos donde stock es 0 o undefined
8. ✅ Inicializar múltiples veces para asegurar que funcione
9. ✅ Agregar logs de debug

## Información adicional

- **Framework**: Django
- **Frontend**: HTML/CSS/JavaScript vanilla (sin frameworks)
- **Productos**: Vienen de dos fuentes:
  - Base de datos (modelo `Sahumerio` con `pk`)
  - Archivo Excel (con `idx`)
- **Stock**: Algunos productos pueden tener `stock = 0` o no tener stock definido
- **Navegador**: El problema ocurre en diferentes navegadores

## Lo que necesito

1. **Diagnóstico**: Identificar por qué algunos productos no funcionan y otros sí
2. **Solución**: Código JavaScript robusto que funcione para TODOS los productos
3. **Explicación**: Entender la causa raíz del problema

## Preguntas específicas

- ¿Puede ser un problema de timing en la inicialización?
- ¿Puede haber conflictos entre múltiples inicializaciones?
- ¿El problema está relacionado con productos de DB vs Excel?
- ¿Hay algún problema con los IDs o selectores CSS?
- ¿El problema está en el frontend o backend?

## Archivos relevantes

- `templates/catalogo.html` - Template principal con el HTML y JavaScript
- `cart/views.py` - Vista que maneja `cart_add()`
- `cart/cart.py` - Clase Cart que maneja la lógica del carrito
- `appcoder/views.py` - Vista `CatalogoExcelView` que genera el contexto

## Código JavaScript actual (resumen)

```javascript
(function() {
  'use strict';
  if (window.catalogInitialized) return;
  window.catalogInitialized = true;
  
  function syncQuantity(card) { /* sincroniza input con hidden */ }
  function addToCart(form) { /* envía AJAX request */ }
  
  function initCatalog() {
    // Inicializa selectores de cantidad
    document.querySelectorAll('.quantity-selector').forEach(...)
    // Inicializa formularios
    document.querySelectorAll('.add-to-cart-form').forEach(...)
  }
  
  // Inicialización múltiple
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCatalog);
  } else {
    setTimeout(initCatalog, 100);
  }
  setTimeout(initCatalog, 500);
})();
```

## Resultado esperado

Un código JavaScript que:
- ✅ Funcione para TODOS los productos sin excepciones
- ✅ Permita cambiar la cantidad con los botones + y -
- ✅ Agregue la cantidad correcta al carrito
- ✅ Sea robusto y no tenga problemas de timing
- ✅ No tenga conflictos entre múltiples inicializaciones
- ✅ Maneje correctamente productos de DB y Excel
- ✅ Funcione incluso si el stock es 0 o undefined

---

**Por favor, analiza el problema y proporciona una solución completa y robusta.**

