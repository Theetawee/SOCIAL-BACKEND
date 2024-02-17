from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import NotificationSerializer
from rest_framework import generics
from .models import Notification
from django.db.models import Q



class NotificationList(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        user_notifications=Notification.objects.filter(Q(to_user=user)|Q(is_read=False))
        return user_notifications

notifications=NotificationList.as_view()



@api_view(["GET"])
def notifications_seen(request,pk):
    notification=Notification.objects.get(pk=pk)
    notification.is_read=True
    notification.save()

    return Response({"message": "success"}, status=status.HTTP_200_OK)
