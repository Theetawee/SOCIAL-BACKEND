import re

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .settings import accounts_config


def validate_username(username: str) -> tuple:
    """A function that validates the username.

    Args:
        username (str): The username to validate.

    Returns:
        tuple: A tuple containing a boolean indicating if the username is valid
            and a string containing the error message if the username is invalid.
    """
    if len(username) < accounts_config.USERNAME_MIN_LENGTH:
        return (
            False,
            f"Username should be at least {accounts_config.USERNAME_MIN_LENGTH} characters long.",
        )

    if username in accounts_config.DISALLOWED_USERNAMES:
        return False, f"Username must not contain the word '{username}'."

    # Check for allowed characters (letters, numbers, and underscores)
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username should only contain letters, numbers, and underscores."

    # Check for maximum length
    if len(username) > 30:
        return False, "Username should not exceed 30 characters."

    return True, ""


def password_validator(password: str, user=None) -> tuple:
    """
    A function that validates the password.

    Args:
        password (str): The password to validate.
        user (User, optional): The user associated with the password. Defaults to None.

    Returns:
        tuple: A tuple containing the validated password and a boolean indicating
        if the password is valid.
    """

    try:
        # Run Django's built-in password validators
        validate_password(password, user)

        # Add any additional custom validation rules
        if not (
            any(char.isdigit() for char in password)
            and any(char.isupper() for char in password)
            and any(char.islower() for char in password)
        ):
            return password, False

    except ValidationError:
        return password, False

    return password, True
