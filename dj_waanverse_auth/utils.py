import random
import string
import threading
from importlib import import_module

from django.conf import settings
from django.contrib.auth.models import update_last_login
from django.contrib.auth.signals import user_logged_in
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from .messages import Messages
from .models import EmailAddress, EmailConfirmationCode, MultiFactorAuth
from .settings import accounts_config


def set_cookie(response: HttpResponse, name: str, value: str, max_age: int, **kwargs):
    """
    Set a cookie on the response with given parameters.

    Parameters:
    - response (HttpResponse): The response object to set the cookie on.
    - name (str): The name of the cookie.
    - value (str): The value of the cookie.
    - max_age (int): The maximum age of the cookie in seconds.
    - kwargs: Additional parameters for setting the cookie (e.g., path, domain, secure, httponly, samesite).
    """
    response.set_cookie(
        name,
        value,
        max_age=max_age,
        path=kwargs.get("path", accounts_config.COOKIE_PATH),
        domain=kwargs.get("domain", accounts_config.COOKIE_DOMAIN),
        secure=kwargs.get("secure", accounts_config.COOKIE_SECURE_FLAG),
        httponly=kwargs.get("httponly", accounts_config.COOKIE_HTTP_ONLY_FLAG),
        samesite=kwargs.get("samesite", accounts_config.COOKIE_SAMESITE_POLICY),
    )
    return response


def set_cookies(
    response: HttpResponse,
    access_token: str = None,
    refresh_token: str = None,
    mfa: str = None,
) -> HttpResponse:
    """
    Set cookies on the response object for access token, refresh token, and MFA.

    Parameters:
    - response (HttpResponse): The response object to set the cookies on.
    - access_token (str): The access token to set in the cookie (optional).
    - refresh_token (str): The refresh token to set in the cookie (optional).
    - mfa (str): The MFA authentication ID to set in the cookie (optional).

    Returns:
    - HttpResponse: The modified response object with cookies set.
    """
    if access_token:
        access_token_lifetime = api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()
        set_cookie(
            response,
            accounts_config.ACCESS_TOKEN_COOKIE,
            access_token,
            max_age=int(access_token_lifetime),
        )

    if refresh_token:
        refresh_token_lifetime = api_settings.REFRESH_TOKEN_LIFETIME.total_seconds()
        set_cookie(
            response,
            accounts_config.REFRESH_TOKEN_COOKIE,
            refresh_token,
            max_age=int(refresh_token_lifetime),
        )

    if mfa:
        mfa_lifetime = accounts_config.MFA_COOKIE_DURATION.total_seconds()
        set_cookie(
            response, accounts_config.MFA_COOKIE_NAME, mfa, max_age=int(mfa_lifetime)
        )

    return response


class EmailThread(threading.Thread):
    def __init__(self, context, email, subject, template):
        self.context = context
        self.email = email
        self.subject = subject
        self.template = template
        threading.Thread.__init__(self)

    def run(self):
        dispatch_email(self.context, self.email, self.subject, self.template)


def dispatch_email(context, email, subject, template):
    """
    Sends an email to the specified email

    Args:
        context (any): The context of the email which will be passed to the template
        email (str): The email address to which the email will be sent
        subject (str): The subject of the email
        template (str): The name of the template located in the 'emails' folder
    """
    context["PLATFORM_NAME"] = accounts_config.PLATFORM_NAME
    template_name = f"emails/{template}.html"
    convert_to_html_content = render_to_string(
        template_name=template_name, context=context
    )
    plain_message = strip_tags(convert_to_html_content)
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[
                email,
            ],
            html_message=convert_to_html_content,
            fail_silently=False,
        )
    except Exception as e:
        raise ValueError(f"Could not send an email. Error: {e}")


def handle_email_mechanism(context, email, subject, template):
    """
    Handles email sending by deciding whether to use threading or not
    based on the EMAIL_THREADING_ENABLED setting.

    Args:
        context (any): The context of the email which will be passed to the template
        email (str): The email address to which the email will be sent
        subject (str): The subject of the email
        template (str): The name of the template located in the 'emails' folder
    """
    if accounts_config.EMAIL_THREADING_ENABLED:
        email_thread = EmailThread(context, email, subject, template)
        email_thread.start()
    else:
        dispatch_email(context, email, subject, template)


def handle_email_verification(user):
    """Generates and sends the email verification code to the user's email.

    Args:
        user (User): The user to which the email verification code will be sent.

    Returns:
        EmailConfirmationCode: The email verification code.
    """
    length = accounts_config.CONFIRMATION_CODE_DIGITS

    # Generate a numeric code
    code = "".join(random.choices(string.digits, k=length))

    try:
        user_code, created = EmailConfirmationCode.objects.get_or_create(user=user)
        user_code.code = code
        user_code.save()
        handle_email_mechanism(
            context={
                "code": code,
                "timespan": accounts_config.EMAIL_VERIFICATION_CODE_DURATION,
            },
            email=user.email,
            subject=Messages.verify_email_subject,
            template="verify_email",
        )

    except Exception as e:
        raise ValueError({"msg": f"Could not create a confirmation code. Error: {e}"})

    return user_code


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def generate_password_reset_code():
    length = accounts_config.CONFIRMATION_CODE_LENGTH

    # Generate a numeric code
    code = "".join(random.choices(string.digits, k=length))

    return code


def get_serializer(path):
    """Dynamically import and return serializer"""

    serializer_module, serializer_class = path.rsplit(".", 1)
    module = import_module(serializer_module)
    return getattr(module, serializer_class)


def user_email_address(user):
    """
    Get or create the email address for the user.

    Args:
        user (User): The user object to get or create the email address for.

    Returns:
        EmailAddress: The email address object for the user.
    """
    email_address, created = EmailAddress.objects.get_or_create(user=user, primary=True)

    if created:
        email_address.primary = True
        email_address.email = user.email
        email_address.save()

    return email_address


def reset_response(response: HttpResponse) -> HttpResponse:
    """
    Remove the refresh and access token cookies from the response.

    Args:
        response (Response): The response object to remove the cookies from.
    """
    response.delete_cookie(accounts_config.ACCESS_TOKEN_COOKIE)
    response.delete_cookie(accounts_config.REFRESH_TOKEN_COOKIE)

    return response


def get_email_verification_status(user):
    """
    Checks if the email address associated with the user is verified.

    Args:
        user (User): The user object to check.

    Returns:
        bool: True if the email address is verified, False otherwise.
    """
    email_address = user_email_address(user)
    if email_address and email_address.verified:
        return True
    return False


def handle_user_login(context, user):
    """
    Handle user login.

    Args:
        context (any): The context object passed to the signal handler.
        user (User): The user object that was logged in.
    """
    user_logged_in.send(
        sender=user.__class__,
        request=context["request"],
        user=user,
    )
    update_last_login(None, user)


def check_mfa_status(user):
    """
    Checks if the user has MFA enabled.

    Args:
        user (User): The user object to check

    Returns:
        bool: True if MFA is enabled, False otherwise
    """
    try:
        account_mfa = MultiFactorAuth.objects.get(account=user)
        return account_mfa.activated
    except MultiFactorAuth.DoesNotExist:
        return False


def generate_tokens(user, refresh_token=None):
    """
    Generates access and refresh tokens for the given user.

    Args:
        user (User): The user object to generate tokens for.

    Returns:
        dict: A dictionary containing the access and refresh tokens.
    """
    if refresh_token:
        refresh = RefreshToken(refresh_token)
    else:
        refresh = RefreshToken.for_user(user)
    UserClaimsSerializer = get_serializer(accounts_config.USER_CLAIM_SERIALIZER_CLASS)
    serializer = UserClaimsSerializer(user)
    claims = serializer.data
    for key, value in claims.items():
        refresh[key] = value

    return {"refresh_token": str(refresh), "access_token": str(refresh.access_token)}


def get_user_agent(request):
    """
    Get the user agent from the request.

    Args:
        request (Request): The request object.

    Returns:
        str: The user agent string.
    """
    return request.META.get("HTTP_USER_AGENT", "<unknown>")[:255]
