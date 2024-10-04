import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import blurhash
from cloudinary.uploader import destroy, upload
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image


def upload_profile_image(file, file_name, folder=None, request=None):
    """
    Upload image to Cloudinary in production, or handle locally in development.
    Always name the image after the file_name and overwrite if it exists.

    Args:
        file (_file_): The file to upload.
        file_name (str): The file_name to use as the image name.
        folder (str, optional): The folder to upload the image to in Cloudinary.
        request (HttpRequest, optional): The request object to build absolute URLs.

    Returns:
        url: str
    """
    # Construct the public ID using the folder and file_name
    public_id = f"{folder}/{file_name}" if folder else file_name

    if settings.DEBUG:
        file_name = f"{file_name}_{file.name}"
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
        response = upload(
            file,
            public_id=public_id,
            overwrite=True,
            folder=folder,
        )
        return response["secure_url"]


def upload_single_image(file, folder=None, request=None):
    """
    Upload a single image to Cloudinary or handle locally in development.
    Give the image a random unique name to avoid overwriting any existing ones.
    """
    # Reset the file pointer to the beginning in case it was read before
    file.seek(0)

    unique_name = f"{uuid.uuid4()}_{file.name}"

    if settings.DEBUG:
        file_path = os.path.join(folder, unique_name) if folder else unique_name
        file_name = default_storage.save(file_path, file)
        relative_url = default_storage.url(file_name)

        if request:
            file_url = request.build_absolute_uri(relative_url)
        else:
            base_url = settings.SITE_URL
            file_url = urljoin(base_url, relative_url)

        return file_url
    else:
        # Reset the file pointer again for production upload
        file.seek(0)

        response = upload(
            file,
            public_id=f"{folder}/{unique_name}" if folder else unique_name,
            overwrite=False,
            folder=folder,
        )
        return response["secure_url"]


def upload_images(files, folder=None, request=None):
    """
    Upload multiple images concurrently to Cloudinary or locally in development.

    Args:
        files (list): List of file objects to upload.
        folder (str, optional): The folder to upload the image to.
        request (HttpRequest, optional): Request object to build absolute URLs (in development).

    Returns:
        list: List of uploaded image URLs.
    """
    # Use ThreadPoolExecutor to upload multiple images concurrently
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(upload_single_image, file, folder, request)
            for file in files
        ]
        results = [future.result() for future in futures]

    return results


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


def delete_images_from_cloudinary(image_urls):
    """
    Delete a list of images from Cloudinary concurrently.

    Args:
        image_urls (list): List of image URLs to delete.

    Returns:
        None
    """
    if not settings.DEBUG:

        def delete_single_image(image_url):
            # Extract the public ID from the image URL (assuming standard Cloudinary URL structure)
            public_id = image_url.split("/")[-1].split(".")[0]
            try:
                # Delete the image from Cloudinary using the public ID
                destroy(public_id)
            except Exception as e:
                # Optionally log the error or handle it
                print(f"Error deleting image {image_url}: {e}")

        # Use ThreadPoolExecutor to delete images concurrently
        with ThreadPoolExecutor() as executor:
            executor.map(delete_single_image, image_urls)
