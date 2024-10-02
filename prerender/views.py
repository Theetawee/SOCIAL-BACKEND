from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import truncatechars

from accounts.models import Account
from main.models import Post


def index(request):
    posts_list = Post.objects.all()
    paginator = Paginator(posts_list, 10)  # Show 10 posts per page

    page_number = request.GET.get(
        "page"
    )  # Get the current page number from the request
    posts = paginator.get_page(page_number)  # Get the posts for that page

    context = {
        "title": "Alloqet: Your Social Network, Reimagined",
        "description": "Alloqet is more than just a social network. It's a place where communities thrive and friendships are formed. Connect with like-minded individuals, share your passions, and discover exciting new content on Alloqet.",
        "og_url": "https://alloqet.com",
        "posts": posts,
    }
    return render(request, "main/index.html", context=context)


def profile_view(request, username):
    account = get_object_or_404(Account, username=username)

    context = {
        "title": f"{account.name} (@{account.username}) on Alloqet",
        "description": f"Discover valuable insights, expertise, and contributions from {account.name} (@{account.username}) on Alloqet. Connect, learn, and engage with their latest posts and activities.",
        "account": account,
        "og_image": account.get_image,
        "og_url": f"https://alloqet.com/{account.username}",
    }

    return render(request, "main/profile.html", context=context)


def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    truncated_content = truncatechars(post.content.strip(), 50)

    context = {
        "title": f"{truncated_content} - {post.author.name} on Alloqet",
        "description": f"{truncatechars(post.content.strip(), 150)} - Read more from {post.author.name} and explore their insights and expertise on Alloqet.",
        "og_url": f"https://alloqet.com/status/{post_id}",
        "post": post,
    }

    return render(request, "main/post_detail.html", context=context)


def login_view(request):
    context = {
        "title": "Login | Alloqet",
        "description": "Sign in to Alloqet to access your personalized account, connect with others, and explore valuable content. Stay engaged with the latest insights and discussions.",
        "og_url": "https://alloqet.com/i/login",
    }
    return render(request, "accounts/login.html", context=context)


def signup_view(request):
    context = {
        "title": "Join Alloqet - Your Hub for Social Learning & Discovery",
        "description": "Create your Alloqet account today and start engaging with a vibrant community. Learn, share, and connect with experts and friends on our innovative social platform.",
    }
    return render(request, "main/signup.html", context=context)


def search_view(request):
    query = request.GET.get("q")
    posts = accounts = None
    results = False

    if query:
        # Search posts by content and accounts by name or username
        posts = Post.objects.filter(
            Q(content__icontains=query) | Q(author__username__icontains=query)
        )[:5]
        accounts = Account.objects.filter(
            Q(name__icontains=query)
            | Q(username__icontains=query)
            | Q(bio__icontains=query)
        )[:5]
    if posts or accounts:
        results = True
    # Set title and description based on the search query
    title = f"Search results for '{query}' on Alloqet" if query else "Search on Alloqet"
    description = f"Explore posts and accounts matching '{query}' on Alloqet, the platform for learning, sharing, and connecting with a vibrant community."

    context = {
        "query": query,
        "posts": posts,
        "accounts": accounts,
        "title": title,
        "description": description,
        "results": results,
    }
    return render(request, "main/search.html", context=context)
