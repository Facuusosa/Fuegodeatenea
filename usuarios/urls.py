from django.urls import path, reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from .views import login_view, registro_view, perfil_view, logout_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("registro/", registro_view, name="registro"),
    path("logout/", logout_view, name="logout"),  # <-- tu vista
    path("perfil/", perfil_view, name="perfil"),
    path(
        "password-change/",
        PasswordChangeView.as_view(
            template_name="password_change_form.html",
            success_url=reverse_lazy("password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "password-change/done/",
        PasswordChangeDoneView.as_view(template_name="password_change_done.html"),
        name="password_change_done",
    ),
]
