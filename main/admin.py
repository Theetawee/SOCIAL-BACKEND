from django.contrib import admin

from .models import Feedback, Post

admin.site.register(Post)
admin.site.register(Feedback)
