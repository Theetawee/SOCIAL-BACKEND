from .models import Notification


def create_notification(sender, receiver, type, post=None):
    new_notification = Notification.objects.create(
        from_user=sender, to_user=receiver, notification_type=type, post=post
    )
    new_notification.save()
