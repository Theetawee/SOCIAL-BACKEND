from rest_framework import serializers
from .models import Post
from accounts.serializers import BasicAccountSerializer


class PostSerializer(serializers.ModelSerializer):
    author = BasicAccountSerializer(read_only=True)

    class Meta:
        model = Post
        fields = "__all__"
