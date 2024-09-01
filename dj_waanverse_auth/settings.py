from datetime import timedelta
from typing import List, Optional, TypedDict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class AccountConfigSchema(TypedDict, total=False):
    AUTH_METHODS: List[str]
    MFA_RECOVERY_CODES_COUNT: int
    ACCESS_TOKEN_COOKIE: str
    REFRESH_TOKEN_COOKIE: str
    COOKIE_PATH: str
    COOKIE_DOMAIN: Optional[str]
    COOKIE_SAMESITE_POLICY: str
    COOKIE_SECURE_FLAG: bool
    COOKIE_HTTP_ONLY_FLAG: bool
    MFA_COOKIE_NAME: str
    MFA_COOKIE_DURATION: timedelta
    USER_CLAIM_SERIALIZER_CLASS: str
    REGISTRATION_SERIALIZER_CLASS: str
    USERNAME_MIN_LENGTH: int
    DISALLOWED_USERNAMES: List[str]
    USER_DETAIL_SERIALIZER_CLASS: str
    ENABLE_EMAIL_ON_LOGIN: bool
    CONFIRMATION_CODE_DIGITS: int
    PLATFORM_NAME: str
    EMAIL_VERIFICATION_CODE_DURATION: int
    MFA_ISSUER_NAME: str
    MFA_CODE_DIGITS: int
    MFA_EMAIL_ALERTS_ENABLED: bool
    PASSWORD_RESET_CODE_DURATION: timedelta
    PASSWORD_RESET_COOLDOWN_PERIOD: timedelta
    PASSWORD_RESET_MAX_ATTEMPTS: int
    EMAIL_THREADING_ENABLED: bool
    USE_ADMIN_PANEL: bool
    USE_UNFOLD: bool
    AUTO_RESEND_EMAIL: bool


class AccountConfig:
    def __init__(self, settings_dict: AccountConfigSchema):
        self.AUTH_METHODS = settings_dict.get("AUTH_METHODS", ["username"])
        self.MFA_RECOVERY_CODES_COUNT = settings_dict.get(
            "MFA_RECOVERY_CODES_COUNT", 10
        )
        self.ACCESS_TOKEN_COOKIE = settings_dict.get(
            "ACCESS_TOKEN_COOKIE", "access_token"
        )
        self.REFRESH_TOKEN_COOKIE = settings_dict.get(
            "REFRESH_TOKEN_COOKIE", "refresh_token"
        )
        self.COOKIE_PATH = settings_dict.get("COOKIE_PATH", "/")
        self.COOKIE_DOMAIN = settings_dict.get("COOKIE_DOMAIN", None)
        self.COOKIE_SAMESITE_POLICY = settings_dict.get("COOKIE_SAMESITE_POLICY", "Lax")
        self.COOKIE_SECURE_FLAG = settings_dict.get("COOKIE_SECURE_FLAG", False)
        self.COOKIE_HTTP_ONLY_FLAG = settings_dict.get("COOKIE_HTTP_ONLY_FLAG", True)
        self.MFA_COOKIE_NAME = settings_dict.get("MFA_COOKIE_NAME", "mfa_token")
        self.MFA_COOKIE_DURATION = settings_dict.get(
            "MFA_COOKIE_DURATION", timedelta(minutes=2)
        )
        self.USER_CLAIM_SERIALIZER_CLASS = settings_dict.get(
            "USER_CLAIM_SERIALIZER_CLASS",
            "dj_waanverse_auth.serializers.BasicAccountSerializer",
        )
        self.REGISTRATION_SERIALIZER_CLASS = settings_dict.get(
            "REGISTRATION_SERIALIZER_CLASS",
            "dj_waanverse_auth.serializers.SignupSerializer",
        )
        self.USERNAME_MIN_LENGTH = settings_dict.get("USERNAME_MIN_LENGTH", 4)
        self.DISALLOWED_USERNAMES = settings_dict.get(
            "DISALLOWED_USERNAMES", ["waanverse"]
        )

        self.USER_DETAIL_SERIALIZER_CLASS = settings_dict.get(
            "USER_DETAIL_SERIALIZER_CLASS",
            "dj_waanverse_auth.serializers.AccountSerializer",
        )
        self.ENABLE_EMAIL_ON_LOGIN = settings_dict.get("ENABLE_EMAIL_ON_LOGIN", True)
        self.CONFIRMATION_CODE_DIGITS = settings_dict.get("CONFIRMATION_CODE_DIGITS", 6)
        self.PLATFORM_NAME = settings_dict.get("PLATFORM_NAME", "Waanverse Auth")
        self.EMAIL_VERIFICATION_CODE_DURATION = settings_dict.get(
            "EMAIL_VERIFICATION_CODE_DURATION", 10
        )  # in minutes
        self.MFA_ISSUER_NAME = settings_dict.get(
            "MFA_ISSUER_NAME", "Waanverse Labs Inc."
        )
        self.MFA_CODE_DIGITS = settings_dict.get("MFA_CODE_DIGITS", 6)
        self.MFA_EMAIL_ALERTS_ENABLED = settings_dict.get(
            "MFA_EMAIL_ALERTS_ENABLED", True
        )
        self.PASSWORD_RESET_CODE_DURATION = settings_dict.get(
            "PASSWORD_RESET_CODE_DURATION", timedelta(minutes=10)
        )
        self.PASSWORD_RESET_COOLDOWN_PERIOD = settings_dict.get(
            "PASSWORD_RESET_COOLDOWN_PERIOD", timedelta(minutes=5)
        )
        self.PASSWORD_RESET_MAX_ATTEMPTS = settings_dict.get(
            "PASSWORD_RESET_MAX_ATTEMPTS", 1
        )
        self.EMAIL_THREADING_ENABLED = settings_dict.get(
            "EMAIL_THREADING_ENABLED", True
        )

        self.USE_ADMIN_PANEL = settings_dict.get("USE_ADMIN_PANEL", False)
        self.USE_UNFOLD = settings_dict.get("USE_UNFOLD", False)
        self.AUTO_RESEND_EMAIL = settings_dict.get("AUTO_RESEND_EMAIL", False)


# Merge user-provided settings with the default settings
USER_SETTINGS = getattr(settings, "WAANVERSE_AUTH", {})
accounts_config = AccountConfig({**AccountConfigSchema(), **USER_SETTINGS})


# Ensure email settings are configured if necessary
required_email_settings = [
    "EMAIL_HOST",
    "EMAIL_PORT",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
    "EMAIL_USE_TLS",
]

for setting in required_email_settings:
    if not getattr(settings, setting, None):
        raise ImproperlyConfigured(
            f"Email setting '{setting}' is required but not configured. Refer to django docs (https://docs.djangoproject.com/en/5.1/topics/email/)"
        )


if accounts_config.USE_UNFOLD and "unfold" not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured(
        "If 'USE_UNFOLD' is set to True, 'unfold' must be in INSTALLED_APPS"
    )
