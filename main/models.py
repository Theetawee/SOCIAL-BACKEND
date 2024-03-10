from django.db import models
from accounts.models import Account
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models.signals import post_save
from django.dispatch import receiver
import blurhash
from PIL import Image

# Create your models here.


class Base(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    content = models.TextField()
    likes = models.ManyToManyField(Account, related_name="%(class)s_likes", blank=True)
    dislikes = models.ManyToManyField(
        Account, related_name="%(class)s_dislikes", blank=True
    )
    views = models.PositiveIntegerField(default=0)
    taged_accounts = models.ManyToManyField(
        Account, blank=True, related_name="%(class)s_tagged"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def timestamp(self):
        return naturaltime(self.created_at)

    def is_liked(self, user):
        return self.likes.filter(pk=user.pk).exists()

    def is_disliked(self, user):
        return self.dislikes.filter(pk=user.pk).exists()

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_comments(self):
        return Comment.objects.filter(post=self).count()

    def __str__(self):
        return self.content[:40]

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class Post(Base):
    pass


class Comment(Base):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    pass


class ContentImage(models.Model):
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, blank=True, null=True, related_name="comment_content_images"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="content_images", blank=True, null=True
    )
    content_image = models.ImageField(upload_to="media/")

    image_hash = models.CharField(max_length=300, blank=True, null=True)


@receiver(post_save, sender=ContentImage)
def create_image_hash(sender, instance, created, **kwargs):
    if created:
        if instance.content_image:
            with Image.open(instance.content_image) as image:
                image.thumbnail((100, 100))
                hash = blurhash.encode(image, x_components=4, y_components=3)
                instance.image_hash = hash
                instance.save()
