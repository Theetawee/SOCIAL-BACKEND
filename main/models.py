from django.db import models
from accounts.models import Account
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db.models.signals import post_save
from django.dispatch import receiver
import blurhash
from PIL import Image
from django.urls import reverse

# Create your models here.


class Base(models.Model):
    CONTENTTYPE = (("Post", "Post"), ("Comment", "Comment"))
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    content = models.TextField()
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content_type = models.CharField(max_length=255, choices=CONTENTTYPE, default="Post")
    likes = models.ManyToManyField(Account, blank=True, related_name="%(class)s_likes")

    @property
    def creation_date(self):
        return naturaltime(self.created_at)

    def __str__(self):
        return f"Post-{self.id}"

    def get_absolute_url(self):
        return reverse("post", kwargs={"pk": self.pk})

    def total_likes(self):
        return self.likes.all().count()

    def is_liked(self, user):
        if user in self.likes.all():
            return True
        return False

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class Post(Base):
    taged_accounts = models.ManyToManyField(
        Account, blank=True, related_name="taged_posts"
    )

    @property
    def is_bookmarked(self, user):
        if Bookmark.objects.filter(account=user, post=self).exists():
            return True
        return False

    @property
    def total_bookmarks(self):
        return Bookmark.objects.filter(post=self).count()

    @property
    def total_comments(self):
        return Comment.objects.filter(post=self).count()


class Comment(Base):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )


class ContentImage(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="comment_content_images",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="content_images",
        blank=True,
        null=True,
    )
    content_image = models.ImageField(upload_to="media/")

    image_hash = models.CharField(max_length=300, blank=True, null=True)


class Bookmark(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.account.username} bookmarked Post-{self.post.id}"


@receiver(post_save, sender=ContentImage)
def create_image_hash(sender, instance, created, **kwargs):
    if created:
        if instance.content_image:
            with Image.open(instance.content_image) as image:
                image.thumbnail((100, 100))
                hash = blurhash.encode(image, x_components=4, y_components=3)
                instance.image_hash = hash
                instance.save()
