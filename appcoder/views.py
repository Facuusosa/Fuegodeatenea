from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.conf import settings
from pathlib import Path
from .models import Sahumerio
from .forms import SahumerioForm
import pandas as pd
import unicodedata, re
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


def _leer_excel():
    ruta = Path(settings.BASE_DIR) / "final.xlsx"
    if not ruta.exists():
        return []
    try:
        df = pd.read_excel(ruta).fillna("")
    except Exception:
        return []
    cols = list(df.columns)
    col_marca    = _pick_col(cols, "marca", "brand")
    col_titulo   = _pick_col(cols, "titulo","nombre","producto","material","sahumerio")
    col_desc     = _pick_col(cols, "descripcion","descripción","detalle","desc")
    col_precio   = _pick_col(cols, "precio","valor","importe")
    col_duracion = _pick_col(cols, "duracion","duración")
    col_imagen   = _pick_col(cols, "imagenes","imagen","image","foto","pic")
    name_lut, stem_lut = _index_product_files()
    items = []
    for i, r in df.iterrows():
        marca = str(r.get(col_marca, "")).strip()
        titulo = str(r.get(col_titulo, "")).strip()
        descripcion = str(r.get(col_desc, "")).strip()
        precio = r.get(col_precio, "")
        duracion = str(r.get(col_duracion, "")).strip()
        imgs_raw = str(r.get(col_imagen, "")).strip()
        first_val = ""
        if imgs_raw:
            partes = [p.strip() for p in re.split(r"[;,]", imgs_raw) if p.strip()]
            first_val = partes[0] if partes else ""
        img_file, img_abs = _parse_img_cell(first_val, name_lut, stem_lut)
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
        items.append({
            "idx": i,
            "marca": marca,
            "titulo": titulo,
            "descripcion": descripcion,
            "precio": precio,
            "duracion": duracion,
            "img_file": img_file,
            "img_abs": img_abs,
            "raw": first_val,
        })
    return items


class CatalogoExcelView(TemplateView):
    template_name = "catalogo.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        x_items = _leer_excel()
        edit_mode = (
            self.request.user.is_authenticated
            and self.request.user.username.lower() == "fsosa"
            and self.request.GET.get("modo") == "edit"
        )
        db_qs = Sahumerio.objects.all()
        db_items = []
        for o in db_qs:
            # CORRECCIÓN: Usar imagen_resuelta() para obtener la imagen correcta (Cloudinary o local)
            img_url = o.imagen_resuelta()
            
            # Determinar si es file local o URL absoluta
            img_file = ""
            img_abs = ""
            
            if img_url:
                # Si es una URL de Cloudinary o externa (empieza con http:// o https://)
                if img_url.startswith(('http://', 'https://')):
                    img_abs = img_url
                # Si viene de ImageField local (/media/)
                elif img_url.startswith('/media/') or img_url.startswith(settings.MEDIA_URL):
                    img_abs = img_url
                # Si es una ruta relativa, es un archivo local
                else:
                    img_file = img_url
            
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
                "raw": "",
                "marca": getattr(o, "marca", "") or "",
            })
        qs = db_qs.values("id", "nombre", "marca")
        lut = {}
        for q in qs:
            n = q["nombre"] or ""
            m = q["marca"] or ""
            for k in {_norm_text(n), _norm_text(f"{m} {n}"), _norm_text(f"{n} {m}")}:
                lut[k] = q["id"]
        for it in x_items:
            it["origen"] = "XLSX"
            it["pk"] = None
            it["match_id"] = lut.get(_norm_text(it["titulo"]))
        combinados = x_items + db_items
        def _key(x):
            a = (x.get("marca") or "").lower()
            b = (x.get("titulo") or "").lower()
            return (a, b)
        combinados.sort(key=_key)
        ctx["items"] = combinados
        ctx["edit_mode"] = edit_mode
        ctx["debug"] = bool(self.request.GET.get("debug"))
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
