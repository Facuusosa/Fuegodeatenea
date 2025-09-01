from django.http import HttpResponseForbidden

class OnlyFsosaAdminMiddleware:
    """
    Permite acceso a /admin/ sólo si el usuario logueado es 'fsosa'.
    Cualquier otro usuario (o anónimo) recibe 403.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        if path.startswith("/admin/"):
            user = getattr(request, "user", None)
            if not (user and user.is_authenticated and user.username.lower() == "fsosa"):
                return HttpResponseForbidden("Acceso a admin restringido")
        return self.get_response(request)
