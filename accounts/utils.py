import secrets
import hashlib
from .models import Account, UserDevice
from django.utils import timezone
from device_detector import DeviceDetector


def generate_secure_key(length=64):
    while True:
        random_bytes = secrets.token_bytes(length)
        random_hex = hashlib.sha256(random_bytes).hexdigest()

        if not Account.objects.filter(access_key=random_hex).exists():
            return random_hex


def set_device(user, request):
    device = DeviceDetector(request.headers.get("User-Agent")).parse()

    os_name = device.os_name()
    os_version = device.os_version()
    engine = device.engine()

    device_brand = device.device_brand()
    device_model = device.device_model()
    device_type = device.device_type()
    client_name = device.client_name()
    client_type = device.client_type()
    client_version = device.client_version()

    # Check if a UserDevice instance already exists for the user
    user_device, created = UserDevice.objects.get_or_create(
        user=user,
        defaults={
            "os_name": os_name,
            "os_version": os_version,
            "engine": engine,
            "device_brand": device_brand,
            "device_model": device_model,
            "device_type": device_type,
            "client_name": client_name,
            "client_type": client_type,
            "client_version": client_version,
        },
    )

    user_device.last_used = timezone.now()
    user_device.save()
