from django.contrib.auth import get_user_model
from django.db import models

Account = get_user_model()


class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    views = models.IntegerField(default=0)

    # For handling retweets
    original_post = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="retweets",
    )
    tagged_accounts = models.ManyToManyField(
        Account, related_name="tagged_posts", blank=True
    )
    # Fields for tracking interactions
    likes = models.ManyToManyField(Account, related_name="liked_posts", blank=True)

    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}"

    class Meta:
        ordering = ("-created_at",)


class Media(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    file = models.FileField(upload_to="post_media/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Media for {self.post}"


class Follow(models.Model):
    follower = models.ForeignKey(
        Account, related_name="following", on_delete=models.CASCADE
    )
    followed = models.ForeignKey(
        Account, related_name="followers", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed")

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"
