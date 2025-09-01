from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Sahumerio

# Nuevo mixin: solo fsosa
class SoloFsosaMixin(UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return u.is_authenticated and u.username.lower() == "fsosa"

class SahumerioLista(ListView):
    model = Sahumerio
    template_name = "catalogo.html"
    context_object_name = "object_list"


class SahumerioDetalle(DetailView):
    model = Sahumerio
    template_name = "sahumerio_detalle.html"
    context_object_name = "object"

# ABM solo para fsosa
class SahumerioCrear(LoginRequiredMixin, SoloFsosaMixin, CreateView):
    model = Sahumerio
    fields = ["marca", "nombre", "descripcion", "stock", "precio", "imagen"]
    template_name = "sahumerio_form.html"
    success_url = reverse_lazy("sahumerios_lista")

class SahumerioEditar(LoginRequiredMixin, SoloFsosaMixin, UpdateView):
    model = Sahumerio
    fields = ["marca", "nombre", "descripcion", "stock", "precio", "imagen"]
    template_name = "sahumerio_form.html"
    success_url = reverse_lazy("sahumerios_lista")

class SahumerioBorrar(LoginRequiredMixin, SoloFsosaMixin, DeleteView):
    model = Sahumerio
    template_name = "sahumerio_confirm_delete.html"
    success_url = reverse_lazy("sahumerios_lista")
