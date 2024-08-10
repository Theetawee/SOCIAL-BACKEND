from rest_framework import serializers
from .models import Post
from accounts.serializers import BasicAccountSerializer
from accounts.models import Account


class PostSerializer(serializers.ModelSerializer):
    author = BasicAccountSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        write_only=True,
        required=True,
    )

    class Meta:
        model = Post
        fields = [
            "id",
            "content",
            "author",
            "author_id",
            "created_at",
            "updated_at",
            "parent",
            "original_post",
            "likes",
        ]

    def create(self, validated_data):
        author_id = validated_data.pop("author_id")
        post = Post.objects.create(author_id=author_id, **validated_data)
        return post

    def update(self, instance, validated_data):
        instance.content = validated_data.get("content", instance.content)
        instance.parent = validated_data.get("parent", instance.parent)
        instance.original_post = validated_data.get(
            "original_post", instance.original_post
        )
        instance.likes = validated_data.get("likes", instance.likes)
        instance.save()
        return instance

    def validate(self, data):
        # Add any custom validation logic here
        return data
