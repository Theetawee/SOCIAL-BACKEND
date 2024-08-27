from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.models import Account

from .serializers import BasicAccountSerializer


class UserList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BasicAccountSerializer
    pagination_class = None

    def get_queryset(self):
        username = self.request.query_params.get("username", None)

        if username:
            return Account.objects.filter(username__icontains=username)[:5]
        return Account.objects.none()


user_list = UserList.as_view()
