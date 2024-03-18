from .models import Notification


def create_notification(sender, receiver, type):
    new_notification = Notification.objects.create(
        from_user=sender, to_user=receiver, notification_type=type
    )
    new_notification.save()
