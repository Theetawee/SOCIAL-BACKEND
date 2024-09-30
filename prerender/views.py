from urllib.parse import unquote

from django.shortcuts import HttpResponse, get_object_or_404
from rest_framework.serializers import ModelSerializer

from .models import ScrapedContent


class HTMLSerializer(ModelSerializer):
    class Meta:
        model = ScrapedContent
        fields = ["content"]


def render_scraped_content(request, url):
    content = get_object_or_404(ScrapedContent, url=unquote(url))
    return HttpResponse(content.content, content_type="text/html")
