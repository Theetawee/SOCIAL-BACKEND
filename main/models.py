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


class Reaction(models.Model):
    REACTION_CHOICES = [
        ("anger", "Anger"),
        ("laughing", "Laughing"),
        ("sad", "Sad"),
        ("disbelief", "Disbelief"),
        ("love", "Love"),
        ("thumbs-up", "ThumbsUp"),
        ("thumbs-down", "ThumbsDown"),
    ]

    post = models.ForeignKey(Post, related_name="reactions", on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=50, choices=REACTION_CHOICES)

    def __str__(self):
        return f"Post: {self.post.id} {self.user.username} reacted with {self.emoji}"

    class Meta:
        unique_together = ("post", "user", "emoji")  # Prevent duplicate reactions


class ImageMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media")
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    image_hash = models.CharField(max_length=255)

    def __str__(self):
        return f"Image for {self.post.id}"


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


class Feedback(models.Model):
    rating = models.CharField(max_length=5)
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"feedback-{self.id}"
