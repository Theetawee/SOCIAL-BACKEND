from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

Account = get_user_model()


class AuthBackend(ModelBackend):
    """
    Custom authentication backend that allows authentication using email, username, or phone number.
    """

    def authenticate(self, request, login_field=None, password=None, **kwargs):
        if login_field is None or password is None:
            return None

        # Query the user by email, username, or phone_number
        try:
            user = Account.objects.get(
                Q(email=login_field) | Q(username=login_field) | Q(phone=login_field)
            )
        except Account.DoesNotExist:
            return None

        # Check if the password is correct
        if user.check_password(password):
            return user
        return None
