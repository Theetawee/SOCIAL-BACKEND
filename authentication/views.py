from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import LoginSerializer
from .utils import set_cookie


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data, context={"request": request})

    if serializer.is_valid():
        # Get the validated data, which includes tokens and user info
        response = Response(data=serializer.validated_data, status=status.HTTP_200_OK)

        # Set access and refresh tokens as cookies in the response
        set_cookie(response, serializer.validated_data["access"], "access")
        set_cookie(response, serializer.validated_data["refresh"], "refresh")

        return response

    # Return errors if the validation fails
    return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
