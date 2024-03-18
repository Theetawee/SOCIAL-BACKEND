from django.db import models

# Create your models here.


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ("like", "like"),
        ("comment", "comment"),
        ("follow", "follow"),
    )
    from_user = models.ForeignKey(
        "accounts.Account", on_delete=models.CASCADE, related_name="from_user"
    )
    to_user = models.ForeignKey(
        "accounts.Account", on_delete=models.CASCADE, related_name="to_user"
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.from_user.username} - {self.notification_type}'
