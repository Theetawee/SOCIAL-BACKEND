import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from urllib.parse import urljoin

import blurhash
from cloudinary.uploader import destroy, upload
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image


def convert_and_save_image(file, file_name):
    """
    Convert the image to WebP format and save locally or return the content.
    Args:
        file (_file_): The file to convert and save.
        file_name (str): The name to use for the converted file.

    Returns:
        ContentFile: Optimized image in WebP format for saving in local storage.
    """
    # Convert image to WebP using Pillow
    img = Image.open(file)
    buffer = BytesIO()
    img.save(buffer, format="WEBP", optimize=True, quality=85)

    return ContentFile(buffer.getvalue(), name=f"{file_name}.webp")


def handle_image_upload(file, file_name, folder=None, request=None, overwrite=True):
    """
    Handle image upload either to Cloudinary or local storage based on DEBUG mode.
    Args:
        file (_file_): The file to upload.
        file_name (str): The file name to use.
        folder (str, optional): The folder where the image should be saved.
        request (HttpRequest, optional): The request object for building URLs (optional).
        overwrite (bool, optional): Whether to overwrite the file in Cloudinary (default: True).

    Returns:
        str: The URL of the uploaded image.
    """
    if settings.DEBUG:
        # Save locally and convert to WebP
        webp_file = convert_and_save_image(file, file_name)
        file_path = os.path.join(folder, webp_file.name) if folder else webp_file.name
        saved_file = default_storage.save(file_path, webp_file)
        relative_url = default_storage.url(saved_file)

        # Generate absolute URL if `request` is provided
        if request:
            file_url = request.build_absolute_uri(relative_url)
        else:
            base_url = settings.SITE_URL
            file_url = urljoin(base_url, relative_url)
    else:
        # Cloudinary upload with optimization
        file.seek(0)
        response = upload(
            file,
            public_id=f"{folder}/{file_name}" if folder else file_name,
            overwrite=overwrite,
            folder=folder,
            format="webp",  # Convert to WebP in Cloudinary
            quality="auto",  # Automatically optimize quality based on Cloudinary's algorithms
            resource_type="image",  # Ensure the upload is treated as an image
        )
        file_url = response["secure_url"]

    return file_url


def upload_profile_image(file, file_name, folder=None, request=None):
    """
    Upload image to Cloudinary in production or handle locally in development.
    Always name the image after the file_name and overwrite if it exists.
    """
    return handle_image_upload(file, file_name, folder, request, overwrite=True)


def upload_single_image(file, folder=None, request=None):
    """
    Upload a single image with a unique name to Cloudinary or handle locally in development.
    """
    unique_name = f"{uuid.uuid4()}"
    return handle_image_upload(file, unique_name, folder, request, overwrite=False)


def upload_images(files, folder=None, request=None):
    """
    Upload multiple images concurrently to Cloudinary or locally in development.
    """
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
