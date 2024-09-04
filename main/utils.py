import cloudinary.uploader
import os
from django.core.files.storage import default_storage
from django.conf import settings
from urllib.parse import urljoin


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
        return response["url"]
