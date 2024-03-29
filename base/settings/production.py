# flake8: noqa


from base.settings.base import *


SECRET_KEY = os.environ.get("SECRET_KEY")

# ALLOWED_HOSTS = ["api.waanverse.com", "waanverse.onrender.com"]
DEBUG = False
ALLOWED_HOSTS = ["*"]

try:
    PRIVATE_KEY_PATH = "/etc/secrets/private_key.pem"
    PUBLIC_KEY_PATH = "/etc/secrets/public_key.pem"

    with open(PRIVATE_KEY_PATH, "r") as private_key_file:
        PRIVATE_KEY = private_key_file.read()
    with open(PUBLIC_KEY_PATH, "r") as public_key_file:
        PUBLIC_KEY = public_key_file.read()
except Exception:
    PRIVATE_KEY = ""
    PUBLIC_KEY = ""

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PGDATABASE"),
        "USER": os.environ.get("PGUSER"),
        "PASSWORD": os.environ.get("PGPASSWORD"),
        "HOST": os.environ.get("PGHOST"),
        "PORT": os.environ.get("PGPORT", 5432),
        "OPTIONS": {
            "sslmode": "require",
        },
    }
}

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": "dodcxvbqu",
    "API_KEY": "926972112538678",
    "API_SECRET": os.environ.get("STORAGE_SECRET"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

STATIC_URL = "https://theetawee.github.io/social_app_files/"


CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = ["https://www.waanverse.com", "https://api.waanverse.com","https://abs.waanverse.com"]


GOOGLE_REDIRECT_URI = "https://www.waanverse.com/accounts/oauth2/google/"


ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"


BACKUP_DIRECTORY = os.path.join(BASE_DIR, "backups/production")


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.zoho.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "accounts@waanverse.com"
EMAIL_HOST_PASSWORD = os.environ.get("NEMAIL_PASSWORD")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False


CSRF_TRUSTED_ORIGINS = [
    "https://api.waanverse.com, https://www.waanverse.com",
    "https://waanverse.com",
    "https://abs.waanverse.com",
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    # 'disable_existing_loggers': False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "INFO",
        },
        "django.server": {
            "handlers": ["django.server"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "EMAIL_AUTHENTICATION": True,
        "APP": {
            "client_id": "414400776439-npsvquoa24a34ehbgvu3d1ni923rl6jh.apps.googleusercontent.com",
            "secret": os.environ.get("PROD_GOOGLE_SECRET"),
            "key": "",
        },
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "offline",
        },
        "FETCH_USERINFO": True,
    }
}

EMAIL_VERIFICATION_URL = "https://www.waanverse.com/accounts/"


REST_AUTH["JWT_AUTH_SECURE"] = True
REST_AUTH["JWT_AUTH_COOKIE_DOMAIN"] = ".waanverse.com"


SIMPLE_JWT["SIGNING_KEY"] = PRIVATE_KEY
SIMPLE_JWT["VERIFYING_KEY"] = PUBLIC_KEY
