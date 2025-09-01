from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import Registro

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"]
            )
            if user:
                login(request, user)
                messages.success(request, f"¡Bienvenid@, {user.username}!")
                return redirect("sahumerios_lista")
    else:
        form = AuthenticationForm()
    return render(request, "iniciar_sesion.html", {"form": form})

def registro_view(request):
    if request.method == "POST":
        form = Registro(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cuenta creada. Iniciá sesión para continuar.")
            return redirect("login")
    else:
        form = Registro()
    return render(request, "registro.html", {"form": form})

def logout_view(request):  
    logout(request)
    messages.success(request, "Cerraste sesión. ¡Hasta la próxima!")
    return redirect("sahumerios_lista")

@login_required
def perfil_view(request):
    return render(request, "perfil.html")
