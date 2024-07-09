from django.db import models
from taggit.managers import TaggableManager
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.dispatch import receiver
import blurhash
from PIL import Image
from django_ckeditor_5.fields import CKEditor5Field


def validate_minimum_size(image, width=300, height=300):
    error = False
    if width is not None and image.width < width:
        error = True
    if height is not None and image.height < height:
        error = True
    if error:
        raise ValidationError([f"Size should be at least {width} x {height} pixels."])


def validate_image_size(fieldfile_obj):
    filesize = fieldfile_obj.file.size
    megabyte_limit = 2.0
    if filesize > megabyte_limit * 1024 * 1024:
        raise ValidationError("Max file size is %sMB" % str(megabyte_limit))


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField(max_length=400)
    slug = models.SlugField(max_length=200, blank=True, null=True, unique=True)
    content = CKEditor5Field("Text", config_name="extends")
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, blank=True, null=True
    )
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        "accounts.Account", on_delete=models.CASCADE, blank=True, null=True
    )
    featured = models.BooleanField(default=False)
    cover_image = models.ImageField(
        upload_to="articles/",
        blank=True,
        null=True,
        validators=[validate_minimum_size, validate_image_size],
    )
    image_alt = models.CharField(max_length=200, blank=True, null=True)
    image_hash = models.CharField(
        max_length=200, default="LEHV6nWB2yk8pyo0adR*.7kCMdnj"
    )
    tags = TaggableManager(blank=True)

    def __str__(self):
        return self.title

    def image(self):
        if self.cover_image:
            return self.cover_image.url
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        image_file = self.cover_image
        with Image.open(image_file) as image:
            image.thumbnail((100, 100))
            hash_value = blurhash.encode(image, x_components=4, y_components=3)
            self.image_hash = hash_value

        super().save(*args, **kwargs)


@receiver(pre_save, sender=Article)
def create_article_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)
        # Ensure slug is unique
        while Article.objects.filter(slug=instance.slug).exists():
            instance.slug = f"{instance.slug}-{instance.id}"


@receiver(pre_save, sender=Category)
def create_category_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)
        # Ensure slug is unique
        while Category.objects.filter(slug=instance.slug).exists():
            instance.slug = f"{instance.slug}-{instance.id}"
