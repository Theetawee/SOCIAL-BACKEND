from django.contrib.auth import get_user_model
from django.utils.text import slugify

Account = get_user_model()


def get_username(user_info):
    """Generate a unique username from user_info.

    Args:
        user_info (dict): User information from Google API.

    Returns:
        str: A unique username.
    """

    # Attempt to generate a username from the email
    email = user_info.get("email")
    if email:
        username = slugify(email.split("@")[0])
    else:
        # Fallback to using the given name if email is not available
        given_name = user_info.get("given_name", "")
        if given_name:
            username = slugify(given_name)
        else:
            # If no email or given name, generate a default username
            username = "waanie"

    # Ensure the username is unique
    original_username = username
    counter = 1
    while Account.objects.filter(username=username).exists():
        username = f"{original_username}{counter}"
        counter += 1

    return username


def get_serializer_fields(serializer_class):
    """Retrieve the field names from a serializer class.

    Args:
        serializer_class (serializers.Serializer): The serializer class.

    Returns:
        list: A list of field names defined in the serializer.
    """
    serializer = serializer_class()
    return list(serializer.fields.keys())
