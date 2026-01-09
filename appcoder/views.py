from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.conf import settings
from django.templatetags.static import static
from django.core.cache import cache
from pathlib import Path
from .models import Sahumerio
from .forms import SahumerioForm
import pandas as pd
import unicodedata, re
import random
from difflib import SequenceMatcher


class SoloFsosaMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and u.username.lower() == "fsosa"


def _norm_text(s: str) -> str:
    s = str(s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", s)


def _pick_col(cols, *needles):
    norm_cols = { _norm_text(c): c for c in cols }
    for n in needles:
        n = _norm_text(n)
        if n in norm_cols:
            return norm_cols[n]
    for nc, orig in norm_cols.items():
        if any(k in nc for k in ["imagen","image","foto","pic"]):
            return orig
    return None


def _index_product_files():
    prod_dir = Path(settings.BASE_DIR) / "static" / "img" / "productos"
    name_lut = {}
    stem_lut = {}
    if prod_dir.exists():
        for p in prod_dir.iterdir():
            if p.is_file():
                name_lut[p.name.lower()] = p.name
                stem_lut[_norm_text(p.stem)] = p.name
    return name_lut, stem_lut


def _resolve_local_image(name: str, name_lut: dict, stem_lut: dict) -> str:
    if not name:
        return ""
    s = str(name).strip().strip("'\"").replace("\\", "/")
    if "?" in s:
        s = s.split("?", 1)[0]
    s = s.split("/")[-1]
    low = s.lower()
    if low in name_lut:
        return name_lut[low]
    base = Path(s).stem
    for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        cand = (base + ext).lower()
        if cand in name_lut:
            return name_lut[cand]
    key = _norm_text(base)
    if key in stem_lut:
        return stem_lut[key]
    best_name = ""
    best_score = 0.0
    for stem, fname in stem_lut.items():
        if key in stem or stem in key:
            best_name = fname
            best_score = 1.0
            break
        score = SequenceMatcher(None, key, stem).ratio()
        if score > best_score:
            best_score = score
            best_name = fname
    return best_name if best_score >= 0.6 else ""


def _parse_img_cell(cell: str, name_lut: dict, stem_lut: dict):
    s = str(cell or "").strip().strip("'\"").replace("\\", "/")
    if not s:
        return "", ""
    if "?" in s:
        s = s.split("?", 1)[0]
    if s.lower().startswith(("http://", "https://")):
        return "", s
    sl = s.lstrip("/").lower()
    for pref in ("static/", "img/productos/", "productos/"):
        if sl.startswith(pref):
            s = s[len(pref):]
            break
    s = s.split("/")[-1]
    return _resolve_local_image(s, name_lut, stem_lut), ""


def _parse_stock(value):
    """Convierte el valor de stock a número entero."""
    if pd.isna(value) or value == "" or value is None:
        return 0
    try:
        return int(float(str(value)))
    except (ValueError, TypeError):
        return 0


def _parse_activo(value):
    """Determina si el producto está activo."""
    if pd.isna(value) or value == "" or value is None:
        return True
    
    val_str = str(value).strip().upper()
    
    if val_str in ("NO", "N", "FALSE", "0", "INACTIVO", "INACTIVE"):
        return False
    
    if val_str in ("SI", "S", "YES", "Y", "TRUE", "1", "ACTIVO", "ACTIVE"):
        return True
    
    return True


def _reconstruir_nombre_imagen(row, col_imagenes):
    """Reconstruye el nombre completo de la imagen concatenando columnas Imagen 1-12"""
    partes = []
    
    for col in col_imagenes:
        valor = str(row.get(col, "")).strip()
        if valor and valor != "-" and not pd.isna(valor):
            partes.append(valor)
    
    if not partes:
        return ""
    
    nombre_completo = "".join(partes)
    nombre_completo = nombre_completo.replace(" ", "").replace("-", "")
    
    if not any(nombre_completo.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
        nombre_completo += ".jpg"
    
    return nombre_completo


def _leer_excel():
    # Intentar obtener del cache primero (TTL: 1 hora)
    cached_data = cache.get('productos_excel')
    if cached_data is not None:
        return cached_data

    ruta = Path(settings.BASE_DIR) / "final.xlsx"
    if not ruta.exists():
        return []
    try:
        df = pd.read_excel(ruta).fillna("")
    except Exception:
        return []
    
    cols = list(df.columns)
    col_marca    = _pick_col(cols, "marca", "brand")
    col_titulo   = _pick_col(cols, "titulo","nombre","producto","material","sahumerio", "concatena nombre", "concatenacion")
    col_desc     = _pick_col(cols, "descripcion","descripción","detalle","desc")
    col_precio   = _pick_col(cols, "precio","valor","importe")
    col_duracion = _pick_col(cols, "duracion","duración")
    col_stock    = _pick_col(cols, "stock", "cantidad", "existencia")
    col_activo   = _pick_col(cols, "activo", "active", "estado", "status")
    
    col_imagenes = []
    for i in range(1, 13):
        col_name = f"Imagen {i}"
        if col_name in cols:
            col_imagenes.append(col_name)
    
    name_lut, stem_lut = _index_product_files()
    items = []
    
    for i, r in df.iterrows():
        marca = str(r.get(col_marca, "")).strip()
        titulo = str(r.get(col_titulo, "")).strip()
        descripcion = str(r.get(col_desc, "")).strip()
        precio = r.get(col_precio, "")
        duracion = str(r.get(col_duracion, "")).strip()
        
        stock = _parse_stock(r.get(col_stock, ""))
        activo = _parse_activo(r.get(col_activo, ""))
        
        # Optimización: ignorar productos inactivos y sin stock
        if not activo and stock <= 0:
             continue

        nombre_imagen_completo = _reconstruir_nombre_imagen(r, col_imagenes)
        
        img_file = ""
        img_abs = ""
        
        if nombre_imagen_completo:
            img_file, img_abs = _parse_img_cell(nombre_imagen_completo, name_lut, stem_lut)
        
        if not img_file and not img_abs and titulo:
            key = _norm_text(titulo)
            if key in stem_lut:
                img_file = stem_lut[key]
            else:
                best_name = ""
                best_score = 0.0
                for stem, fname in stem_lut.items():
                    if key in stem or stem in key:
                        best_name = fname
                        best_score = 1.0
                        break
                    score = SequenceMatcher(None, key, stem).ratio()
                    if score > best_score:
                        best_score = score
                        best_name = fname
                if best_score >= 0.6:
                    img_file = best_name
        
        img_url = ""
        if img_abs:
            img_url = img_abs
        elif img_file:
            img_url = static(f"img/productos/{img_file}")
        else:
            img_url = static("img/placeholder.png")
        
        items.append({
            "idx": i,
            "marca": marca,
            "titulo": titulo,
            "descripcion": descripcion,
            "precio": precio,
            "duracion": duracion,
            "img_file": img_file,
            "img_abs": img_abs,
            "img_url": img_url,
            "raw": nombre_imagen_completo,
            "stock": stock,
            "activo": activo,
        })
    
    # Guardar en cache
    cache.set('productos_excel', items, 3600)
    return items


class CatalogoExcelView(TemplateView):
    template_name = "catalogo.html"
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # Leer productos del Excel (con cache)
        x_items = _leer_excel()
        
        # Leer productos de la DB (Optimizado: solo activos)
        db_qs = Sahumerio.objects.filter(activo=True)
        db_items = []
        
        for o in db_qs:
            img_url = ""
            if hasattr(o, 'imagen_resuelta'):
                img_url = o.imagen_resuelta()
            elif hasattr(o, 'imagen') and o.imagen:
                img_url = str(o.imagen.url) if hasattr(o.imagen, 'url') else str(o.imagen)
            
            img_file = ""
            img_abs = ""
            
            if img_url:
                if img_url.startswith(('http://', 'https://')):
                    img_abs = img_url
                elif img_url.startswith('/media/') or img_url.startswith(settings.MEDIA_URL):
                    img_abs = img_url
                else:
                    img_file = img_url
            
            stock = getattr(o, "stock", 0) or 0
            
            final_img_url = ""
            if img_abs:
                final_img_url = img_abs
            elif img_file:
                final_img_url = static(f"img/productos/{img_file}")
            else:
                final_img_url = static("img/placeholder.png")
            
            db_items.append({
                "origen": "DB",
                "pk": o.pk,
                "id": o.pk,
                "idx": None,
                "titulo": getattr(o, "nombre", "") or "",
                "descripcion": getattr(o, "descripcion", "") or "",
                "precio": float(getattr(o, "precio", 0) or 0),
                "duracion": "",
                "img_file": img_file,
                "img_abs": img_abs,
                "img_url": final_img_url,
                "raw": "",
                "marca": getattr(o, "marca", "") or "",
                "stock": stock,
                "activo": True,
            })
        
        # Lookup para matching
        if x_items and db_items:
            lut = { _norm_text(q["nombre"]): q["id"] for q in db_qs.values("id", "nombre", "marca") }
            for it in x_items:
                it["origen"] = "XLSX"
                it["pk"] = None
                it["match_id"] = lut.get(_norm_text(it["titulo"]))
        else:
             for it in x_items:
                it["origen"] = "XLSX"
                it["pk"] = None
                it["match_id"] = None

        # Combinar
        combinados = x_items + db_items
        
        # 1. BÚSQUEDA por texto
        busqueda = self.request.GET.get('search', '').strip()
        if busqueda:
            busqueda_lower = busqueda.lower()
            combinados = [
                item for item in combinados
                if (busqueda_lower in item.get('titulo', '').lower() or
                    busqueda_lower in item.get('marca', '').lower() or
                    busqueda_lower in item.get('descripcion', '').lower())
            ]
        
        # 2. FILTRO por marca
        marca_activa = self.request.GET.get('marca', '').strip()
        if marca_activa:
            combinados = [
                item for item in combinados 
                if item.get('marca', '').lower() == marca_activa.lower()
            ]
        
        # 3. EXTRAER TODAS LAS MARCAS
        all_items_unfiltered = x_items + db_items
        todas_las_marcas = sorted({
            item.get('marca', '').strip()
            for item in all_items_unfiltered
            if item.get('marca', '').strip()
        })
        
        # Ordenar items
        combinados.sort(key=lambda x: ((x.get("marca") or "").lower(), (x.get("titulo") or "").lower()))
        
        ctx["items"] = combinados
        ctx["marcas"] = todas_las_marcas
        ctx["marca_activa"] = marca_activa
        ctx["search"] = busqueda
        
        return ctx


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # Obtener candidatos para bestsellers
        # 1. Cache
        items = _leer_excel()
        
        # 2. DB (limitado)
        db_promoted = Sahumerio.objects.filter(activo=True).order_by('?')[:4]
        
        # Mezclamos
        bestsellers = []
        
        for o in db_promoted:
            img_url = ""
            if hasattr(o, 'imagen_resuelta'): img_url = o.imagen_resuelta()
            elif hasattr(o, 'imagen') and o.imagen: img_url = o.imagen.url
            
            final_img = img_url if img_url else static("img/placeholder.png")
            
            bestsellers.append({
                "pk": o.pk,
                "titulo": o.nombre,
                "precio": float(o.precio or 0),
                "img_url": final_img,
                "marca": o.marca,
                "origen": "DB",
                "stock": o.stock or 0
            })
            
        # Rellenar con Excel si faltan
        if len(bestsellers) < 4:
            # Tomar algunos aleatorios del Excel que tengan foto
            excel_cands = [x for x in items if (x.get('img_file') or x.get('img_abs')) and x.get('stock',0) > 0]
            if excel_cands:
                sample = random.sample(excel_cands, min(4 - len(bestsellers), len(excel_cands)))
                bestsellers.extend(sample)
        
        ctx['bestsellers'] = bestsellers
        return ctx


class ExcelDetalleView(TemplateView):
    template_name = "sahumerio_detalle_excel.html"
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        items = _leer_excel()
        idx = kwargs.get("idx")
        it = next((x for x in items if x["idx"] == idx), None)
        ctx["it"] = it
        
        match_id = None
        if it:
            qs = Sahumerio.objects.values("id", "nombre", "marca")
            lut = {}
            for q in qs:
                n = q["nombre"] or ""
                m = q["marca"] or ""
                for k in {_norm_text(n), _norm_text(f"{m} {n}"), _norm_text(f"{n} {m}")}:
                    lut[k] = q["id"]
            match_id = lut.get(_norm_text(it["titulo"]))
        
        ctx["match_id"] = match_id
        return ctx


class SahumerioDetalle(DetailView):
    model = Sahumerio
    template_name = "sahumerio_detalle.html"
    context_object_name = "object"


class SahumerioCrear(LoginRequiredMixin, SoloFsosaMixin, CreateView):
    model = Sahumerio
    form_class = SahumerioForm
    template_name = "sahumerio_form.html"
    success_url = reverse_lazy("sahumerios_lista")
    
    def get_initial(self):
        ini = super().get_initial()
        g = self.request.GET
        if g.get("sug_marca"): ini["marca"] = g.get("sug_marca")
        if g.get("sug_nombre"): ini["nombre"] = g.get("sug_nombre")
        if g.get("sug_descripcion"): ini["descripcion"] = g.get("sug_descripcion")
        if g.get("sug_precio"): ini["precio"] = g.get("sug_precio")
        return ini


class SahumerioEditar(LoginRequiredMixin, SoloFsosaMixin, UpdateView):
    model = Sahumerio
    form_class = SahumerioForm
    template_name = "sahumerio_form.html"
    success_url = reverse_lazy("sahumerios_lista")


class SahumerioBorrar(LoginRequiredMixin, SoloFsosaMixin, DeleteView):
    model = Sahumerio
    template_name = "template_confirm_delete.html"
    success_url = reverse_lazy("sahumerios_lista")