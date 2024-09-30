from django.shortcuts import get_object_or_404, render

from accounts.models import Account
from main.models import Post


def index(request):
    context = {
        "title": "Alloqet",
        "description": "Alloqet is an online platform that connects students with qualified local and international experts.",
    }
    posts = Post.objects.all()
    context["posts"] = posts
    return render(request, "main/index.html", context=context)


def profile_view(request, username):
    account = get_object_or_404(Account, username=username)

    context = {
        "title": f"{account.name} (@{account.username}) on Alloqet",
        "description": "Alloqet is an online platform that connects students with qualified local and international experts.",
        "account": account,
    }

    return render(request, "main/profile.html", context=context)
