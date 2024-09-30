from django.conf import settings


def context(request):

    return {
        "base_url": getattr(settings, "BASE_URL", "https://www.alloqet.com"),
    }
