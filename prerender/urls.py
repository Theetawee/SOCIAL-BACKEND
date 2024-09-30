from django.urls import path

from .views import render_scraped_content

urlpatterns = [
    path("render/<path:url>", render_scraped_content, name="render"),
]
