from rest_framework import serializers
from .models import Post
from accounts.serializers import BasicAccountSerializer


class PostSerializer(serializers.ModelSerializer):
    author = BasicAccountSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "content",
            "author",
            "created_at",
            "updated_at",
            "parent",
            "original_post",
            "likes",
        ]


class CreatePostSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)

    def create(self, validated_data):
        user = self.context["request"].user
        post = Post.objects.create(author=user, **validated_data)
        return post

    def save(self, **kwargs):
        validated_data = self.validated_data
        return self.create(validated_data)
