# flake8: noqa

from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]


STATIC_URL = "static/"

MEDIA_URL = "media/"


PRIVATE_KEY_PATH = os.path.join(BASE_DIR, "secrets/private_key.pem")
PUBLIC_KEY_PATH = os.path.join(BASE_DIR, "secrets/public_key.pem")

with open(PRIVATE_KEY_PATH, "r") as private_key_file:
    PRIVATE_KEY = private_key_file.read()
with open(PUBLIC_KEY_PATH, "r") as public_key_file:
    PUBLIC_KEY = public_key_file.read()


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "media"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "static_cdn")

MEDIA_ROOT = os.path.join(BASE_DIR, "media_cdn")

INTERNAL_IPS = [
    "127.0.0.1",
]


CORS_ALLOW_ALL_ORIGINS = True


GOOGLE_REDIRECT_URI = "http://localhost:5173/accounts/oauth2/google/"


ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"


BACKUP_DIRECTORY = os.path.join(BASE_DIR, "backups/development")



SIMPLE_JWT["SIGNING_KEY"] = PRIVATE_KEY
SIMPLE_JWT["VERIFYING_KEY"] = PUBLIC_KEY
