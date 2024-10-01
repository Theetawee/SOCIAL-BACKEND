from django.shortcuts import get_object_or_404, render
from django.template.defaultfilters import truncatechars

from accounts.models import Account
from main.models import Post


def index(request):
    context = {
        "title": "Alloqet: Your Social Network, Reimagined",
        "description": "Alloqet is more than just a social network. It's a place where communities thrive and friendships are formed. Connect with like-minded individuals, share your passions, and discover exciting new content on Alloqet",
        "og_url": "https://alloqet.com",
    }
    posts = Post.objects.all()
    context["posts"] = posts
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
        "title": "Login to Alloqet",
        "description": "Sign in to Alloqet to access your personalized account, connect with others, and explore valuable content. Stay engaged with the latest insights and discussions.",
        "og_url": "https://alloqet.com/i/login",
    }
    return render(request, "main/login.html", context=context)
