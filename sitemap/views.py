from django.contrib.sitemaps import Sitemap
from django.db.models.base import Model

from main.models import Post


class PostSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.5

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj: Model) -> str:
        url = f"/post/{obj.id}"
        return url
