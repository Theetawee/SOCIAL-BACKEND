from .models import Post, ContentImage, Comment, Bookmark
from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from django.db import models


class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }


admin.site.register(Post, PostAdmin)

# admin.site.register(Post)
admin.site.register(ContentImage)
admin.site.register(Comment)
admin.site.register(Bookmark)
