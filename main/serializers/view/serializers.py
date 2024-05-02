from rest_framework import serializers
from accounts.models import Account
from main.models import ContentImage, Post, Comment
from sockets.models import Notification


class PostAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ["username", "image", "id", "profile_image_hash", "verified", "name"]


class ContentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentImage
        fields = ["content_image", "image_hash", "id"]


class PostSerializer(serializers.ModelSerializer):
    account = PostAccountSerializer()
    is_liked = serializers.SerializerMethodField()
    likes = PostAccountSerializer(many=True)
    post_images = ContentImageSerializer(
        many=True, read_only=True, source="content_images"
    )

    class Meta:
        model = Post
        fields = [
            "content",
            "total_likes",
            "account",
            "creation_date",
            "updated_at",
            "id",
            "is_liked",
            "total_comments",
            "post_images",
            "total_bookmarks",
            "views",
            "likes",
        ]

    def get_is_liked(self, obj):
        try:
            user = self.context.get("request").user
            return obj.is_liked(user)
        except Exception as e:
            print(e, "test")
            return False


class CommentSerializer(serializers.ModelSerializer):
    account = PostAccountSerializer()
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()
    taged_accounts = PostAccountSerializer(many=True)
    post_images = ContentImageSerializer(
        many=True, read_only=True, source="comment_content_images"
    )

    class Meta:
        model = Comment
        fields = [
            "content",
            "total_likes",
            "account",
            "created_at",
            "timestamp",
            "updated_at",
            "id",
            "is_liked",
            "is_disliked",
            "taged_accounts",
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


class NotificationSerializer(serializers.ModelSerializer):
    from_user = PostAccountSerializer()
    to_user = PostAccountSerializer()

    class Meta:
        model = Notification
        fields = "__all__"
