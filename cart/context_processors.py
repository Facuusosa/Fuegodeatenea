from decimal import Decimal
from .cart import Cart

def cart_context(request):
    cart = Cart(request)
    cart_items = []
    total = Decimal('0')
    
    # Procesar items del carrito para el template
    for item in cart:
        quantity = int(item.get('quantity', 1))
        price = Decimal(str(item.get('price', 0)))
        subtotal = quantity * price
        
        cart_items.append({
            'id': item.get('id'),
            'name': item.get('name', 'Producto'),
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal,
            'image': item.get('image', ''),
        })
        total += subtotal
    
    return {
        "cart_len": len(cart),
        "cart_total": total,
        "cart_items": cart_items[:3],  # Solo primeros 3 items para el mini carrito
    }