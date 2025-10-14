# settings.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "dev-only"
DEBUG = True
ALLOWED_HOSTS = ["*"]  # Esto permite TODAS las conexiones

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",  # filtros de miles/moneda

    # tus apps
    "appcoder",
    "usuarios",
    "productos",
    "cart",  # carrito
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "Miprimerapaginafsosa.middleware.OnlyFsosaAdminMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "Miprimerapaginafsosa.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cart.context_processors.cart_context",  # badge y total del carrito en toda la app
            ],
        },
    },
]

WSGI_APPLICATION = "Miprimerapaginafsosa.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "es-ar"
TIME_ZONE = "America/Argentina/Buenos_Aires"
USE_I18N = True
USE_TZ = True

# ============================
#  STATIC & MEDIA (IMPORTANTE)
# ============================
# Usar SIEMPRE barra inicial y final
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]      # <BASE_DIR>/static
STATIC_ROOT = BASE_DIR / "staticfiles"        # usado en producción (collectstatic)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"               # <BASE_DIR>/media

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "sahumerios_lista"
LOGOUT_REDIRECT_URL = "sahumerios_lista"

# ============================
#  CONFIGURACIÓN DE SESIONES
# ============================
# Hacer que el carrito persista al cerrar el navegador
SESSION_COOKIE_AGE = 1209600  # 2 semanas (en segundos)
SESSION_SAVE_EVERY_REQUEST = True  # Actualiza la expiración en cada request
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # NO borrar al cerrar navegador
SESSION_COOKIE_NAME = 'sessionid'  # Nombre de la cookie
SESSION_COOKIE_HTTPONLY = True  # Seguridad: no accesible desde JavaScript
SESSION_COOKIE_SAMESITE = 'Lax'  # Protección CSRF

# ============================
#  CARRITO
# ============================
CART_SESSION_ID = "cart"

# WhatsApp (ideal en formato internacional sin +, ej. 54911XXXXXXXX)
WHATSAPP_PHONE = "1168079566"