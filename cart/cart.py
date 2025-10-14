from __future__ import annotations
from decimal import Decimal
from django.conf import settings
from django.templatetags.static import static
from django.contrib.staticfiles import finders


class Cart:
    """
    Carrito almacenado en sesión.

    Estructura en session[self.SESSION_KEY]:
    {
        "<id>": {
            "id": "<id>",
            "name": "Nombre",
            "price": 2800.0,
            "quantity": 2,
            "img": "canela.jpg" | "img/productos/canela.jpg" | "https://...",
            "image_url": "/static/img/productos/canela.jpg" | "https://..." | "/media/...",
            "origin": "DB" | "XLS",
            "is_db": True | False,
        },
        ...
    }
    """

    SESSION_KEY = "cart"

    # --------------------------- utils internas -----------------------------

    @staticmethod
    def _to_decimal(val) -> Decimal:
        try:
            return Decimal(str(val))
        except Exception:
            return Decimal("0")

    @staticmethod
    def _guess_image_url_from_product(product) -> str | None:
        """
        Intenta extraer la URL de imagen de un modelo de BD (ImageField u otros campos típicos).
        ACTUALIZADO: Prioriza imagen_file e imagen_url del modelo Sahumerio.
        """
        # Primero intentar con el método imagen_resuelta() si existe
        if hasattr(product, 'imagen_resuelta'):
            try:
                url = product.imagen_resuelta()
                if url:
                    return url
            except Exception:
                pass
        
        # Lista de candidatos en orden de prioridad
        candidates = (
            "imagen_file",  # Campo principal del modelo Sahumerio
            "imagen_url",   # Campo alternativo del modelo Sahumerio
            "imagen", 
            "image", 
            "foto", 
            "img", 
            "picture", 
            "photo"
        )
        
        for attr in candidates:
            if hasattr(product, attr):
                value = getattr(product, attr)
                if value is None or value == '':
                    continue
                try:
                    # Si es ImageFieldFile tendrá .url
                    url = value.url  # type: ignore[attr-defined]
                except Exception:
                    url = str(value)
                if url:
                    return url
        return None

    @staticmethod
    def _resolve_payload_image_url(img: str | None) -> str | None:
        """
        Normaliza la URL para imágenes que vienen desde Excel/payload.

        Soporta:
          - URLs absolutas (http/https)
          - Rutas /media/... o MEDIA_URL
          - Rutas /static/... o "static/..."
          - Rutas relativas tipo "img/productos/canela.jpg"
          - Solo nombre -> prueba en /static/img/productos/ con extensiones comunes
            y variantes (lowercase, guiones, underscores).
        """
        if not img:
            return None

        s = str(img).strip().replace("\\", "/")
        if not s:
            return None

        # Absoluta
        if s.startswith(("http://", "https://")):
            return s

        # Media
        media_url = getattr(settings, "MEDIA_URL", "/media/")
        if s.startswith("/media/") or (media_url and s.startswith(media_url)):
            return s

        # Static directos
        if s.startswith("/static/"):
            return s
        if s.startswith("static/"):
            return "/" + s

        # Construir lista de candidatos relativos a STATIC
        candidates: list[str] = []

        # Si trae subcarpetas, probar tal cual y variantes
        if "/" in s:
            rel = s.lstrip("/")
            candidates.append(rel)
            candidates.append(rel.lower())
        else:
            # Solo nombre -> empezar por carpeta productos
            candidates.append(f"img/productos/{s}")
            candidates.append(f"img/productos/{s.lower()}")

        # Si no tiene extensión, probar varias + variantes
        name = s.split("/")[-1]
        has_ext = "." in name
        if not has_ext:
            bases = {
                name,
                name.lower(),
                name.replace(" ", "-"),
                name.replace(" ", "_"),
                name.lower().replace(" ", "-"),
                name.lower().replace(" ", "_"),
            }
            exts = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
            for b in bases:
                # si venía con carpeta ya se agregó arriba; acá aseguramos ruta productos
                candidates.append(f"img/productos/{b}")
                for ext in exts:
                    candidates.append(f"img/productos/{b}{ext}")

        # Quitar duplicados preservando orden
        seen = set()
        uniq: list[str] = []
        for rel in candidates:
            rel = rel.replace("\\", "/")
            if rel not in seen:
                seen.add(rel)
                uniq.append(rel)

        # Buscar en el finder de estáticos
        for rel in uniq:
            if finders.find(rel):
                return static(rel)

        # Si no lo encontró, devolver el primero como estático (el <img> caerá a placeholder via onerror)
        return static(uniq[0]) if uniq else None

    # ------------------------------ núcleo ----------------------------------

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(self.SESSION_KEY)
        if cart is None:
            cart = {}
            self.session[self.SESSION_KEY] = cart
        self.cart = cart

    def _save(self):
        self.session[self.SESSION_KEY] = self.cart
        self.session.modified = True

    def add(self, product, quantity: int = 1, replace_quantity: bool = False):
        pid = str(getattr(product, "id"))
        name = getattr(product, "nombre", None) or getattr(product, "name", None) or str(product)
        price = self._to_decimal(getattr(product, "precio", None) or getattr(product, "price", None) or 0)
        
        # CORRECCIÓN: Usar el método mejorado que busca imagen_file e imagen_url
        image_url = self._guess_image_url_from_product(product)

        item = self.cart.get(pid)
        if item is None:
            item = {
                "id": pid,
                "name": name,
                "price": float(price),
                "quantity": 0,
                "img": None,
                "image_url": image_url,
                "origin": "DB",
                "is_db": True,
            }
            self.cart[pid] = item

        if replace_quantity:
            item["quantity"] = max(0, int(quantity))
        else:
            item["quantity"] = max(0, int(item["quantity"]) + int(quantity))

        # refresca datos por si cambiaron
        item["name"] = name
        item["price"] = float(price)
        if image_url:
            item["image_url"] = image_url

        if item["quantity"] <= 0:
            self.cart.pop(pid, None)

        self._save()

    def add_payload(
        self,
        *,
        product_id: str | int,
        name: str,
        price,
        img: str | None = None,
        quantity: int = 1,
        replace_quantity: bool = False,
    ):
        pid = str(product_id)
        price = self._to_decimal(price)
        image_url = self._resolve_payload_image_url(img)

        item = self.cart.get(pid)
        if item is None:
            item = {
                "id": pid,
                "name": name,
                "price": float(price),
                "quantity": 0,
                "img": img,
                "image_url": image_url,
                "origin": "XLS",
                "is_db": False,
            }
            self.cart[pid] = item

        if replace_quantity:
            item["quantity"] = max(0, int(quantity))
        else:
            item["quantity"] = max(0, int(item["quantity"]) + int(quantity))

        # refresca datos
        item["name"] = name or item["name"]
        item["price"] = float(price)
        item["img"] = img
        if image_url:
            item["image_url"] = image_url

        if item["quantity"] <= 0:
            self.cart.pop(pid, None)

        self._save()

    def remove(self, product_id: str | int):
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self._save()

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.session.modified = True
        self.cart = self.session[self.SESSION_KEY]

    def __len__(self):
        return sum(int(i["quantity"]) for i in self.cart.values())

    def __iter__(self):
        """
        Devuelve ítems uniformes y calcula subtotal.
        Garantiza que 'image_url' siempre venga poblado (o placeholder).
        """
        placeholder = static("img/placeholder.svg")  # asegurate de tener este archivo
        for it in list(self.cart.values()):
            qty = int(it.get("quantity", 0))
            price = self._to_decimal(it.get("price", 0))
            subtotal = price * qty
            img_url = it.get("image_url") or self._resolve_payload_image_url(it.get("img")) or placeholder
            yield {
                "id": it.get("id"),
                "name": it.get("name"),
                "price": float(price),
                "quantity": qty,
                "img": it.get("img"),
                "image_url": img_url,
                "origin": it.get("origin", "XLS"),
                "is_db": bool(it.get("is_db")),
                "subtotal": float(subtotal),
            }

    def get_total_price(self) -> float:
        total = Decimal("0")
        for it in self:
            total += Decimal(str(it["subtotal"]))
        return float(total)

    @property
    def total(self) -> float:
        return self.get_total_price()