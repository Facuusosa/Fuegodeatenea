from decimal import Decimal
from django.conf import settings

CART_SESSION_ID = getattr(settings, "CART_SESSION_ID", "cart")

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def _key(self, origin: str, item_id: str | int) -> str:
        return f"{origin}:{item_id}"

    def add_db(self, product, quantity=1, replace_current=False):
        key = self._key("DB", product.id)
        if key not in self.cart:
            self.cart[key] = {
                "origin": "DB",
                "id": str(product.id),
                "title": getattr(product, "nombre", getattr(product, "title", str(product))),
                "brand": getattr(product, "marca", ""),
                "price": str(getattr(product, "precio", "0")),
                "image": getattr(product, "imagen_url", getattr(product, "imagen", "")) or "",
                "quantity": 0,
            }
        if replace_current:
            self.cart[key]["quantity"] = int(quantity)
        else:
            self.cart[key]["quantity"] += int(quantity)
        self.save()

    def add_excel(self, idx: int, title: str, brand: str, price, image="", quantity=1, replace_current=False):
        key = self._key("X", idx)
        if key not in self.cart:
            self.cart[key] = {
                "origin": "X",
                "id": str(idx),
                "title": title,
                "brand": brand or "",
                "price": str(price),
                "image": image or "",
                "quantity": 0,
            }
        if replace_current:
            self.cart[key]["quantity"] = int(quantity)
        else:
            self.cart[key]["quantity"] += int(quantity)
        self.save()

    def remove(self, origin: str, item_id: str | int):
        key = self._key(origin, item_id)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def __iter__(self):
        for item in self.cart.values():
            item["price"] = Decimal(item["price"])
            item["subtotal"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def clear(self):
        self.session[CART_SESSION_ID] = {}
        self.save()

    def save(self):
        self.session.modified = True
