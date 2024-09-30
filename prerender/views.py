from django.shortcuts import get_object_or_404, render

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
        "og_image": account.profile_image_url,
        "og_url": f"https://alloqet.com/{account.username}",
    }

    return render(request, "main/profile.html", context=context)
