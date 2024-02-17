from rest_framework import generics,status
from accounts.serializers import AccountSerializer
from accounts.models import Account
from django.db.models import Q
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def ping(request):
    return Response(status=status.HTTP_200_OK, data={"message": "pong"})




class Search(generics.ListAPIView):
    serializer_class = AccountSerializer

    def get_queryset(self):
        q = self.request.query_params.get("q", "")
        if q == "" or q is None:
            return ""
        results = Account.objects.filter(
            Q(username__icontains=q) | Q(name__icontains=q)
        ).exclude(id=self.request.user.id)
        return results


search = Search.as_view()
