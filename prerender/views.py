from urllib.parse import unquote

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from accounts.models import Account
from main.models import Post

from .models import ScrapedContent
from .scrape import scrape_url


def scrape_view(request):
    # Create a list to hold the URLs to scrape
    urls = ["/", "/i/login", "/i/signup", "/add"]

    # Add post URLs
    urls.extend([f"/status/{post.id}" for post in Post.objects.all()])

    # Add account URLs
    urls.extend([f"/{account.username}" for account in Account.objects.all()])

    results = []

    for url in urls:
        path = f"https://www.alloqet.com{url}"
        try:
            result = scrape_url(path)
            if result:
                # Create or update the scraped content
                new_content, created = ScrapedContent.objects.update_or_create(
                    url=path, defaults={"content": result}
                )
                results.append({"url": url, "content": result})
            else:
                results.append({"url": url, "error": "Failed to scrape the page"})
        except Exception as e:
            results.append({"url": url, "error": str(e)})

    # Return all results as a JSON response
    return JsonResponse({"results": results}, status=200)


def render_scraped_content(request, url):
    content = get_object_or_404(ScrapedContent, url=unquote(url))
    return HttpResponse(content.content)
