from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import LoginSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data, context={"request": request})

    if serializer.is_valid():
        # Return the valid data from the serializer, which includes tokens and user info
        return Response(data=serializer.validated_data, status=status.HTTP_200_OK)

    # Return errors if the validation fails
    return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
