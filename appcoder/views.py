from django.shortcuts import render, redirect
from .models import Celular
from .forms import CelularForm

def celulares_lista(request):
    celulares = Celular.objects.all().order_by('marca', 'modelo')
    return render(request, 'celulares.html', {'celulares': celulares})

def celular_nuevo(request):
    if request.method == 'POST':
        form = CelularForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('celulares')
    else:
        form = CelularForm()
    return render(request, 'formularios/celular_form.html', {'form': form})
