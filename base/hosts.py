from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns(
    "",
    host(r"sitemap", "sitemap.urls", name="sitemap"),
    host(r"(\w+)", settings.ROOT_URLCONF, name="api"),
)
