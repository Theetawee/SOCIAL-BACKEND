from django.urls import path

from .views import render_scraped_content, scrape_view

urlpatterns = [
    path("", scrape_view, name="request"),
    path("render/<path:url>", render_scraped_content, name="render"),
]
