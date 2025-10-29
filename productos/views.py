from django.shortcuts import render
from django.conf import settings
from pathlib import Path
import pandas as pd
from appcoder.views import CatalogoExcelView

def catalogo(request):

    xls = Path(settings.BASE_DIR) / "final.xlsx"
    df = pd.read_excel(xls, sheet_name="HOJA-FINAL").fillna("")

    img_cols = [c for c in df.columns if str(c).strip().lower().startswith("imagen")]

    items = []
    for _, r in df.iterrows():
        marca = str(r.get("Marca","")).strip()
        nombre = str(r.get("Nombre","")).strip()
        titulo = (f"{marca.upper()} {nombre}").strip() or "Producto"

        raw_precio = str(r.get("Precio","")).strip()
        try:
            precio = float(raw_precio.replace(".","").replace(",",".")) if raw_precio else 0.0
        except:
            precio = 0.0
        imagenes = [str(r.get(c,"")).strip() for c in img_cols if str(r.get(c,"")).strip()]

        items.append({
            "titulo": titulo,
            "descripcion": str(r.get("Descripción","")),
            "duracion": str(r.get("DURACION","")),
            "precio": precio,
            "imagenes": imagenes
        })

    items.sort(key=lambda x: x["titulo"])
    return render(request, "catalogo.html", {"items": items})
# Reuse the main catalog view from ``appcoder`` so the context matches the
# expectations of ``templates/catalogo.html`` (origen, idx, pk, etc.).
catalogo = CatalogoExcelView.as_view()

from django.http import HttpResponse
from productos.models import Producto

def test_imagen_url(request):
    p = Producto.objects.first()
    if p and p.imagen:
        return HttpResponse(f"La URL de la imagen es: {p.imagen.url}")
    else:
        return HttpResponse("No se encontró ninguna imagen en productos")
