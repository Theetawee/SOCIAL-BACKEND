from rest_framework import serializers

from accounts.serializers import BasicAccountSerializer
from accounts.models import Account
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author = BasicAccountSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

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
            "comments",
            "views",
            "is_liked",
            "likes_count",
        ]

    def get_comments(self, obj):
        # Return the count of comments that have the current post as their parent
        return Post.objects.filter(parent=obj).count()

    def get_is_liked(self, obj):
        # Get the current user from the context
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        # Check if the user has liked the post
        return obj.likes.filter(id=user.id).exists()

    def get_likes_count(self, obj):
        return len(obj.likes.all())


class CreatePostSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)
    tagged_accounts = serializers.ListField(
        child=serializers.CharField(), required=False
    )

    def create(self, validated_data):
        user = self.context["request"].user
        parent_id = self.context.get("post_id")
        parent = None
        if parent_id:
            try:
                parent = Post.objects.get(id=parent_id)
            except Post.DoesNotExist:
                raise serializers.ValidationError("Parent post does not exist.")

        tagged_accounts = validated_data.pop("tagged_accounts", [])

        # Create the post
        post = Post.objects.create(author=user, parent=parent, **validated_data)

        # Add tagged accounts to the post
        if tagged_accounts:
            tagged_users = Account.objects.filter(username__in=tagged_accounts)
            post.tagged_accounts.add(*tagged_users)

        return post

    def save(self, **kwargs):
        validated_data = self.validated_data
        return self.create(validated_data)
