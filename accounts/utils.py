import secrets
import hashlib
from .models import Account


def generate_secure_key(length=64):
    while True:
        random_bytes = secrets.token_bytes(length)
        random_hex = hashlib.sha256(random_bytes).hexdigest()

        if not Account.objects.filter(access_key=random_hex).exists():
            return random_hex
