from datetime import timedelta
import os
from pathlib import Path
from dotenv import load_dotenv
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY", "django-insecure-vmqe-^x45+go2sj@h-qs&ym7$rr)8(v)t4l81dw(s90o%+ht1s"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Aplicaciones de terceros
    "rest_framework",
    "rest_framework_simplejwt",
    "djoser",
    "corsheaders",
    "drf_spectacular",
    # Aplicaciones locales
    "usuarios",
    "tratamiento",
    "evaluacion_diagnostico",
    "analiticas",
    "agendamiento_citas",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "migraine_app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "migraine_app.wsgi.application"

load_dotenv()
pw = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST")
user = os.getenv("POSTGRES_USER")

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "postgres"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "OPTIONS": {
            "sslmode": "require",
            "connect_timeout": 60,
            "options": "-c statement_timeout=300000",
        },
    }
}
CORS_ALLOW_ALL_ORIGINS = True 
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

DATABASE_ROUTERS = ["migraine_app.routers.CustomRouter"]

# Usuario personalizado
AUTH_USER_MODEL = "usuarios.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

# Djoser
DJOSER = {
    "LOGIN_FIELD": "email",
    "USER_CREATE_PASSWORD_RETYPE": True,
    "SEND_ACTIVATION_EMAIL": False,
    "SEND_CONFIRMATION_EMAIL": False,
    "SERIALIZERS": {
        "user_create": "usuarios.serializers.CrearUsuarioSerializer",
        "user": "usuarios.serializers.UsuarioCompletoSerializer",
        "current_user": "usuarios.serializers.UsuarioCompletoSerializer",
    },
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Email para desarrollo
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Configuración de drf-spectacular para organizar tags
SPECTACULAR_SETTINGS = {
    "TITLE": "Migraine App API",
    "DESCRIPTION": "API completa para la gestión de migrañas y cefaleas",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": False,
    "TAGS": [
        {
            "name": "🔐 Autenticación",
            "description": "Endpoints para autenticación JWT y gestión de sesiones",
        },
        {
            "name": "👥 Usuarios",
            "description": "Gestión de perfiles de usuarios autenticados",
        },
        {"name": "📝 Registro", "description": "Registro público de nuevos usuarios"},
        {
            "name": "📋 Evaluación y diagnóstico",
            "description": "Evaluación y diagnóstico de episodios de cefalea",
        },
    ],
    # Configuración para personalizar tags de endpoints externos
    "PREPROCESSING_HOOKS": [
        "migraine_app.swagger_hooks.custom_preprocessing_hook",
    ],
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": False,
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
        "displayRequestDuration": True,
        "docExpansion": "none",
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "tagsSorter": "alpha",
        "operationsSorter": "alpha",
    },
    "POSTPROCESSING_HOOKS": [
        "migraine_app.swagger_hooks.custom_postprocessing_hook",
    ],
}
