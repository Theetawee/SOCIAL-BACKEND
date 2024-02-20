from rest_framework import serializers
import json
from .models import Post, ContentImage
from accounts.models import Account
from accounts.serializers import AccountSerializer

from rest_framework import serializers
import json
from .models import Post, ContentImage


class CreatePostSerializer(serializers.ModelSerializer):
    content = serializers.CharField(style={"base_template": "textarea.html"})
    taged_accounts = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = ["content", "account", "open_to", "taged_accounts"]

    def create(self, validated_data):
        taged_accounts_data = validated_data.pop("taged_accounts", [])
        files = self.context["request"].FILES.getlist("files")

        # Create the post instance
        post = super(CreatePostSerializer, self).create(validated_data)

        # Handle the list of images if available
        for file_data in files:
            ContentImage.objects.create(post=post, content_image=file_data)

        # Handle tagged accounts
        if taged_accounts_data:
            taged_accounts_data = taged_accounts_data[0]
            taged_accounts_data = json.loads(taged_accounts_data)
            account_id = taged_accounts_data.get("id")
            if account_id:
                tagged_account = Account.objects.get(id=account_id)
                post.taged_accounts.add(tagged_account)

        return post


class ContentImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentImage
        fields = ["content_image", "image_hash", "id"]



class PostAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["username", "image", "id", "profile_image_hash", "verified", "name"]



class PostSerializer(serializers.ModelSerializer):
    account = PostAccountSerializer()
    is_liked = serializers.SerializerMethodField()
    is_disliked = serializers.SerializerMethodField()
    post_images = ContentImageSerializer(
        many=True, read_only=True, source="content_images"
    )

    class Meta:
        model = Post
        fields = [
            "content",
            "total_likes",
            "account",
            "created_at",
            "timestamp",
            "id",
            "is_liked",
            "is_disliked",
            "open_to",
            "total_comments",
            "post_images",
        ]

    def get_is_liked(self, obj):
        user = self.context.get("request").user
        return obj.is_liked(user)

    def get_is_disliked(self, obj):
        user = self.context.get("request").user
        return obj.is_disliked(user)
