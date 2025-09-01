from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Sahumerio

class SahumerioLista(ListView):
    model = Sahumerio
    template_name = "sahumerios.html"
    context_object_name = "sahumerios"

class SahumerioDetalle(DetailView):
    model = Sahumerio
    template_name = "sahumerio_detalle.html"
    context_object_name = "sahumerio"

class SahumerioCrear(CreateView):
    model = Sahumerio
    fields = ["marca", "nombre", "descripcion", "stock", "precio", "imagen_url", "disponible"]
    template_name = "formularios/sahumerio_form.html"
    success_url = reverse_lazy("sahumerios_lista")

class SahumerioEditar(UpdateView):
    model = Sahumerio
    fields = ["marca", "nombre", "descripcion", "stock", "precio", "imagen_url", "disponible"]
    template_name = "formularios/sahumerio_form.html"
    success_url = reverse_lazy("sahumerios_lista")

class SahumerioBorrar(DeleteView):
    model = Sahumerio
    template_name = "formularios/sahumerio_form.html"
    success_url = reverse_lazy("sahumerios_lista")
