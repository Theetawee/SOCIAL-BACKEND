from django.db import models
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime

# Create your models here.
from django.core.exceptions import FieldError


class SubscriptionInfo(models.Model):
    user_agent = models.CharField(max_length=500, blank=True, null=True, unique=True)
    endpoint = models.URLField(max_length=500)
    auth = models.CharField(max_length=100)
    p256dh = models.CharField(max_length=100)


class PushInformation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="webpush_info",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    subscription = models.ForeignKey(
        SubscriptionInfo, related_name="webpush_info", on_delete=models.CASCADE
    )

    def save(self, *args, **kwargs):
        if self.user:
            super(PushInformation, self).save(*args, **kwargs)
        else:
            raise FieldError("At least user or group should be present")


class Notification(models.Model):
    type = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=(
            ("post", "post"),
            ("comment", "comment"),
            ("like", "like"),
            ("follow", "follow"),
            ("mention", "mention"),
        ),
    )
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sender",
        verbose_name="sender",
        on_delete=models.CASCADE,
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="receiver",
        verbose_name="receiver",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    post = models.ForeignKey(
        "posts.Post", on_delete=models.CASCADE, null=True, blank=True
    )
    comment = models.ForeignKey(
        "posts.Comment", on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def timestamp(self):
        return naturaltime(self.created_at)

    def __str__(self):
        return self.from_user.username

    class Meta:
        ordering = ["is_read", "-created_at"]
