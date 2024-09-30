from urllib.parse import unquote

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .models import ScrapedContent


class HTMLSerializer(ModelSerializer):
    class Meta:
        model = ScrapedContent
        fields = ["content"]


@api_view(["GET"])
def render_scraped_content(request, url):
    content = get_object_or_404(ScrapedContent, url=unquote(url))
    data = HTMLSerializer(content).data
    return Response(data=data, status=status.HTTP_200_OK)
