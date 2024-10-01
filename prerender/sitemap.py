from datetime import datetime

from django.contrib.sitemaps import Sitemap
from django.db.models.base import Model

from accounts.models import Account
from main.models import Post


class AccountSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.8

    def items(self):
        return Account.objects.all()

    def lastmod(self, obj):
        return obj.last_login

    def location(self, obj: Model) -> str:
        url = f"/{obj.username}"
        return url


class PostSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.5

    def items(self):
        return Post.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj: Model) -> str:
        url = f"/status/{obj.id}"
        return url


class StaticSitemap(Sitemap):
    changefreq = "daily"  # Optional, frequency of changes
    priority = 1.0  # Optional, priority of the page

    # Define a list of your custom URLs
    def items(self):
        return ["/", "/i/signup", "/i/login"]

    def location(self, item):
        return item

    def lastmod(self, item):
        return datetime.now()
