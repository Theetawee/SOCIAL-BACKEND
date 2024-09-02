# flake8: noqa


from base.settings.base import *

ALLOWED_HOSTS = ["api.alloqet.com"]
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
    "CLOUD_NAME": os.environ.get("IMAGE_CLOUD_NAME"),
    "API_KEY": os.environ.get("IMAGE_CLOUD_KEY"),
    "API_SECRET": os.environ.get("IMAGE_CLOUD_SECRET"),
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

STATIC_URL = "https://theetawee.github.io/social_app_files/"


CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOWED_ORIGINS = ["https://social.alloqet.com"]


ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"


BACKUP_DIRECTORY = os.path.join(BASE_DIR, "backups/production")


CSRF_TRUSTED_ORIGINS = ["https://social.alloqet.com"]


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

SIMPLE_JWT["SIGNING_KEY"] = PRIVATE_KEY
SIMPLE_JWT["VERIFYING_KEY"] = PUBLIC_KEY
