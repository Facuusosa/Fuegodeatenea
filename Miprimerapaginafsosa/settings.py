from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-8k#m9p@x$wv7n2q&5j!h4r*6t^y8u+3d-f_a%b1c#e9g0i2k')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

if 'RAILWAY_ENVIRONMENT' in os.environ:
    ALLOWED_HOSTS = ['*']
elif not DEBUG:
    ALLOWED_HOSTS = ['facuusosa.pythonanywhere.com']
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "appcoder",
    "usuarios",
    "productos",
    "cart",
    'cloudinary_storage',
    'cloudinary',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
                "cart.context_processors.cart_context",
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

# ============================================
# CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS
# ============================================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ============================================
# CONFIGURACIÓN DE ARCHIVOS MEDIA (Subidas)
# ============================================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ============================================
# CONFIGURACIÓN DE CLOUDINARY (Solo para media/uploads)
# ============================================
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

if all(CLOUDINARY_STORAGE.values()):
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    cloudinary.config(**CLOUDINARY_STORAGE)
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    print("⚠️  WARNING: Cloudinary credentials not found - using local media storage")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "sahumerios_lista"
LOGOUT_REDIRECT_URL = "sahumerios_lista"

# ============================================
# CONFIGURACIÓN DE SESIONES
# ============================================
SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

CART_SESSION_ID = "cart"
WHATSAPP_PHONE = "1168079566"

# ============================================
# SEGURIDAD PARA PRODUCCIÓN (Railway + HTTPS)
# ============================================
if not DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_SAMESITE = "Lax"  # ✅ AGREGADO
    CSRF_TRUSTED_ORIGINS = [
        'https://fuegodeatenea.up.railway.app',
        'https://*.railway.app'
    ]  # ✅ AGREGADO
