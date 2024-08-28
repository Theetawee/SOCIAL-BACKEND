from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.models import Account

from .serializers import AccountSerializer, BasicAccountSerializer


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


class UserDetail(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    lookup_field = "username"

    def get_serializer_context(self):
        """Add additional context to the serializer."""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


user_detail = UserDetail.as_view()
