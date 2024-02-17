from django.db import models
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime

# Create your models here.



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
