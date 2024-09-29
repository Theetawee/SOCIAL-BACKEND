from urllib.parse import unquote

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from .models import ScrapedContent
from .scrape import scrape_url


def scrape_view(request):
    url = request.GET.get("url")
    if not url:
        return HttpResponse("URL not provided", status=400)

    try:
        result = scrape_url(url)
        if result:
            # create or update
            new_content, created = ScrapedContent.objects.update_or_create(
                url=url, defaults={"content": result}
            )
            action = "created" if created else "updated"
            print(f"Content {action} for {url}")

            return HttpResponse(result, content_type="text/html")
        else:
            return JsonResponse({"error": "Failed to scrape the page"}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def render_scraped_content(request, url):
    content = get_object_or_404(ScrapedContent, url=unquote(url))

    return HttpResponse(content.content)
