from django import template
from django.urls import reverse

register = template.Library()


@register.simple_tag
def render_url(url_name, *args, **kwargs):
    base_url = "https://www.alloqet.com"
    relative_url = reverse(url_name, args=args, kwargs=kwargs)

    # Trim "prerender" from the URL if it exists
    if relative_url.startswith("/prerender"):
        relative_url = relative_url.replace("/prerender", "", 1)

    return f"{base_url}{relative_url}"
