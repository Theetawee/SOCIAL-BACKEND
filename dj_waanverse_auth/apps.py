# flake8: noqa

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dj_waanverse_auth"
    label = "dj_waanverse_auth"
    verbose_name = "Waanverse Auth"

    def ready(self):
        from .signals import (
            log_user_logged_in_success,
            user_created_via_google,
        )
