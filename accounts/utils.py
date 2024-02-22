import secrets
import hashlib
from .models import Account, UserDevice
from django.utils import timezone

def generate_secure_key(length=64):
    while True:
        random_bytes = secrets.token_bytes(length)
        random_hex = hashlib.sha256(random_bytes).hexdigest()

        if not Account.objects.filter(access_key=random_hex).exists():
            return random_hex




def set_device(user,request):


    # Extract device information
    is_mobile = request.user_agent.is_mobile
    is_tablet = request.user_agent.is_tablet
    is_touch_capable = request.user_agent.is_touch_capable
    browser_family = request.user_agent.browser.family
    browser_version = request.user_agent.browser.version_string
    os_family = request.user_agent.os.family
    os_version = request.user_agent.os.version_string
    device_family = request.user_agent.device.family

    # Check if a UserDevice instance already exists for the user
    user_device, created = UserDevice.objects.get_or_create(
        user=user,
        is_mobile=is_mobile,
        is_tablet=is_tablet,
        is_touch_capable=is_touch_capable,
        browser_family=browser_family,
        browser_version=browser_version,
        os_family=os_family,
        os_version=os_version,
        device_family=device_family,
    )

    user_device.last_used = timezone.now()
    user_device.save()
