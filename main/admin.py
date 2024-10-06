from django.contrib import admin

from .models import Feedback, ImageMedia, Post, Reaction

admin.site.register(Post)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "rating", "feedback", "created_at")


# Register the model with the custom admin
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(ImageMedia)
admin.site.register(Reaction)
