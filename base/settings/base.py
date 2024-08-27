import os
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.environ.get("SECRET_KEY")


AUTH_USER_MODEL = "accounts.Account"


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.sites",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "accounts",
    "main",
    "cloudinary_storage",
    "cloudinary",
    "debug_toolbar",
    "django.contrib.sitemaps",
    "dj_waanverse_auth",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "dj_waanverse_auth.middleware.CookiesHandlerMiddleware",
]

ROOT_URLCONF = "base.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

WSGI_APPLICATION = "base.wsgi.application"


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


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


CORS_ALLOW_CREDENTIALS = True


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("dj_waanverse_auth.backends.JWTAuthentication",),
    "DEFAULT_PAGINATION_CLASS": "base.utils.CustomPageNumberPagination",
    "PAGE_SIZE": 3,
}


AUTHENTICATION_BACKENDS = [
    "dj_waanverse_auth.backends.AuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]


ASGI_APPLICATION = "base.asgi.application"


# SIMPLE_JWT SETTINGS
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "RS256",
}


# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get("SMTP_EMAIL")
EMAIL_HOST_PASSWORD = os.environ.get("SMTP_PASSWORD")
EMAIL_USE_TLS = True


WAANVERSE_AUTH = {
    "USER_CLAIM_SERIALIZER": "accounts.serializers.BasicAccountSerializer",
    "USER_DETAIL_SERIALIZER": "accounts.serializers.BasicAccountSerializer",
    "EMAIL_ON_LOGIN": False,
    "PLATFORM_NAME": "Driblet",
}


GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")
