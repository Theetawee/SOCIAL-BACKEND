from rest_framework import serializers
from accounts.models import Account
from main.models import ContentImage, Post, Comment


class PostAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ["username", "image", "id", "profile_image_hash", "verified", "name"]


class ContentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentImage
        fields = ["content_image", "image_hash", "id"]


class BaseContentSerializer(serializers.ModelSerializer):
    account = PostAccountSerializer()
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()
    taged_accounts = PostAccountSerializer(many=True)
    post_images = ContentImageSerializer(
        many=True, read_only=True, source="content_images"
    )

    class Meta:
        fields = [
            "content",
            "total_likes",
            "account",
            "created_at",
            "timestamp",
            "id",
            "is_liked",
            "is_disliked",
            "taged_accounts",
            "total_comments",
            "post_images",
        ]

    def get_is_liked(self, obj):
        try:
            user = self.context.get("request").user
            return obj.is_liked(user)
        except Exception:
            return False

    def get_is_disliked(self, obj):
        try:
            user = self.context.get("request").user
            return obj.is_disliked(user)
        except Exception:
            return False


class PostSerializer(BaseContentSerializer):

    class Meta(BaseContentSerializer.Meta):
        model = Post


class CommentSerializer(BaseContentSerializer):

    class Meta(BaseContentSerializer.Meta):
        model = Comment



