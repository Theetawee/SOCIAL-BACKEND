import os
import uuid
from urllib.parse import urljoin

import blurhash
import cloudinary.uploader
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image


def upload_profile_image(file, username, folder=None, request=None):
    """
    Upload image to Cloudinary in production, or handle locally in development.
    Always name the image after the username and overwrite if it exists.

    Args:
        file (_file_): The file to upload.
        username (str): The username to use as the image name.
        folder (str, optional): The folder to upload the image to in Cloudinary.
        request (HttpRequest, optional): The request object to build absolute URLs.

    Returns:
        url: str
    """
    # Construct the public ID using the folder and username
    public_id = f"{folder}/{username}" if folder else username

    if settings.DEBUG:
        file_name = f"{username}_{file.name}"
        file_path = os.path.join(folder, file_name) if folder else file_name

        # Save the file locally
        file_name = default_storage.save(file_path, file)
        relative_url = default_storage.url(file_name)

        # Generate absolute URL if `request` is provided
        if request:
            file_url = request.build_absolute_uri(relative_url)
        else:
            # Fallback: Construct absolute URL using site's base URL
            base_url = settings.SITE_URL
            file_url = urljoin(base_url, relative_url)

        return file_url
    else:
        response = cloudinary.uploader.upload(
            file,
            public_id=public_id,
            overwrite=True,
            folder=folder,
        )
        return response["secure_url"]


def upload_image(file, folder=None, request=None):
    """
    Upload image to Cloudinary in production, or handle locally in development.
    Give the image a random unique name to avoid overwriting any existing ones.

    Args:
        file (_file_): The file to upload.
        folder (str, optional): The folder to upload the image to in Cloudinary.
        request (HttpRequest, optional): The request object to build absolute URLs.

    Returns:
        url: str
    """
    # Generate a random unique name using uuid
    unique_name = f"{uuid.uuid4()}_{file.name}"
    file.seek(0)  # Go to the start of the file
    if settings.DEBUG:
        # Save the file locally with the unique name
        file_path = os.path.join(folder, unique_name) if folder else unique_name

        # Save the file using Django's default storage system
        file_name = default_storage.save(file_path, file)
        relative_url = default_storage.url(file_name)

        # Generate absolute URL if `request` is provided
        if request:
            file_url = request.build_absolute_uri(relative_url)
        else:
            # Fallback: Construct absolute URL using site's base URL
            base_url = settings.SITE_URL
            file_url = urljoin(base_url, relative_url)

        return file_url
    else:
        file.seek(0)

        # Upload the file to Cloudinary with the unique name
        response = cloudinary.uploader.upload(
            file,
            public_id=f"{folder}/{unique_name}" if folder else unique_name,
            overwrite=False,  # Ensure it doesn't overwrite any existing files
            folder=folder,
        )
        return response["secure_url"]


def get_image_hash(image):
    """
    Generate BlurHash from an image.

    Args:
        image (_file_): The image to generate the BlurHash from

    Returns:
        str: The BlurHash
    """
    image.seek(0)  # Go to the start of the file

    # Open the image file
    image = Image.open(image)

    # Convert image to RGBA if it has a palette with transparency
    if image.mode == "P" and "transparency" in image.info:
        image = image.convert("RGBA")

    # Process the image (e.g., creating a thumbnail)
    image.thumbnail((100, 100))

    # Generate BlurHash
    hash = blurhash.encode(image, x_components=4, y_components=3)
    return hash
