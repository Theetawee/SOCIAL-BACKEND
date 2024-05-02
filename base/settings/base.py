import os
from datetime import timedelta

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


AUTH_USER_MODEL = "accounts.Account"


# Application definition

INSTALLED_APPS = [
    "daphne",
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
    "dj_rest_auth",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth.registration",
    "allauth.socialaccount.providers.google",
    "main",
    "cloudinary_storage",
    "cloudinary",
    "debug_toolbar",
    "sockets",
    "django.contrib.sitemaps",
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
    "allauth.account.middleware.AccountMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
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
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "base.utils.CustomPageNumberPagination",
    "PAGE_SIZE": 10,
}


# Django allauth
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "accounts.authentication.CustomAuthenticationBackend",
]


ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_CHANGE_EMAIL = False
ACCOUNT_CONFIRM_EMAIL_ON_GET = False
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# ACCOUNT_EMAIL_VERIFICATION = "none"

ACCOUNT_EMAIL_SUBJECT_PREFIX = "Waanverse - "
ACCOUNT_PRESERVE_USERNAME_CASING = False
ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_ADAPTER = "accounts.adapter.CustomAccountAdapter"
ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 60
ACCOUNT_USERNAME_BLACKLIST = ["waanverse"]
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY")
VAPID_ADMIN_EMAIL = "tawee.drake@gmail.com"


ASGI_APPLICATION = "base.asgi.application"


REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "_Waanverse__",
    "JWT_AUTH_REFRESH_COOKIE": "_Secure-RT",
    "JWT_AUTH_RETURN_EXPIRATION": False,
    "REGISTER_SERIALIZER": "accounts.serializers.create.serializers.RegisterSerializer",
    "USER_DETAILS_SERIALIZER": "accounts.serializers.view.serializers.AccountSerializer",
    "PASSWORD_RESET_USE_SITES_DOMAIN": True,
    "OLD_PASSWORD_FIELD_ENABLED": True,
    "JWT_TOKEN_CLAIMS_SERIALIZER": "accounts.serializers.create.serializers.MyTokenObtainPairSerializer",
}


# SIMPLE_JWT SETTINGS
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=35),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=5),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "RS256",
}
