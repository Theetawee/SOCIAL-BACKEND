from django.contrib.auth import user_logged_in, user_login_failed
from django.core.exceptions import ImproperlyConfigured
from django.dispatch import Signal, receiver

from .messages import Messages
from .models import UserLoginActivity
from .settings import accounts_config
from .utils import get_client_ip, get_user_agent, handle_email_mechanism


@receiver(user_logged_in)
def log_user_logged_in_success(sender, user, request, **kwargs):
    try:
        ip_address = get_client_ip(request)
        user_agent_info = (request.META.get("HTTP_USER_AGENT", "<unknown>")[:255],)
        user_login_activity_log = UserLoginActivity(
            login_IP=ip_address,
            login_username=user.username,
            user_agent_info=user_agent_info,
            status=UserLoginActivity.SUCCESS,
        )
        user_login_activity_log.save()

        context = {
            "ip_address": ip_address,
            "username": user.username,
            "user_agent": user_login_activity_log.user_agent_info,
            "email": user.email,
            "time": user_login_activity_log.login_datetime,
        }
        if accounts_config.ENABLE_EMAIL_ON_LOGIN:
            handle_email_mechanism(
                subject=Messages.login_email_subject,
                template="successful_login",
                context=context,
                email=user.email,
            )

    except Exception as e:
        raise ImproperlyConfigured(e)


@receiver(user_login_failed)
def log_user_logged_in_failed(sender, credentials, request, **kwargs):
    try:
        user_agent_info = get_user_agent(request)
        user_login_activity_log = UserLoginActivity(
            login_IP=get_client_ip(request),
            login_username=credentials["username"],
            user_agent_info=user_agent_info,
            status=UserLoginActivity.FAILED,
        )
        user_login_activity_log.save()
    except Exception:
        # log the error
        pass


# Define a custom signal for user creation via Google sign-in
user_created_via_google = Signal()
