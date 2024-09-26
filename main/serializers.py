import json

from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from rest_framework import serializers

from accounts.models import Account
from accounts.serializers import BasicAccountSerializer

from .models import Feedback, ImageMedia, Post
from .utils import get_image_hash, upload_image


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageMedia
        fields = ["image_url", "image_hash", "id"]


class BasicPostSerializer(serializers.ModelSerializer):
    author = BasicAccountSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ["id", "author", "parent", "content"]


class PostSerializer(serializers.ModelSerializer):
    author = BasicAccountSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    natural_time_created = serializers.SerializerMethodField()
    natural_date_created = serializers.SerializerMethodField()
    parent = BasicPostSerializer()
    tagged_accounts = BasicAccountSerializer(many=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "content",
            "author",
            "natural_time_created",
            "natural_date_created",
            "created_at",
            "updated_at",
            "parent",
            "original_post",
            "likes",
            "comments",
            "views",
            "is_liked",
            "likes_count",
            "tagged_accounts",
            "images",
        ]

    def get_comments(self, obj):
        # Return the count of comments that have the current post as their parent
        return Post.objects.filter(parent=obj).count()

    def get_is_liked(self, obj):
        # Get the current user from the context
        request = self.context.get("request")
        if request and not request.user.is_anonymous:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_likes_count(self, obj):
        # Efficiently return the count of likes
        return obj.likes.count()

    def get_natural_time_created(self, obj):
        # Return the natural time (e.g., '10 minutes ago')
        return naturaltime(obj.created_at)

    def get_natural_date_created(self, obj):
        # Return the natural day (e.g., 'today', 'yesterday')
        return naturalday(obj.created_at)

    def get_images(self, obj):
        images = ImageMedia.objects.filter(post=obj)
        return PostImageSerializer(images, many=True).data


class CreatePostSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)
    tagged_accounts = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    files = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True
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

        # Deserialize the 'tagged_accounts' field
        tagged_accounts_str = validated_data.pop("tagged_accounts", "[]")

        # Ensure we're working with a string
        if not isinstance(tagged_accounts_str, str):
            tagged_accounts_str = json.dumps(tagged_accounts_str)

        # Parse the string
        try:
            tagged_accounts = json.loads(tagged_accounts_str)
            # If the result is a list of strings, parse each string
            if isinstance(tagged_accounts, list) and all(
                isinstance(item, str) for item in tagged_accounts
            ):
                tagged_accounts = [json.loads(item) for item in tagged_accounts]
            # Flatten the list if it's a list of lists
            if isinstance(tagged_accounts, list) and all(
                isinstance(item, list) for item in tagged_accounts
            ):
                tagged_accounts = [
                    username for sublist in tagged_accounts for username in sublist
                ]
        except json.JSONDecodeError:
            tagged_accounts = []

        # Ensure the final result is a list
        if not isinstance(tagged_accounts, list):
            tagged_accounts = [tagged_accounts]
        # Extract files from request.FILES (since files are handled separately from validated_data)
        files = validated_data.pop("files", [])
        # Create the post
        post = Post.objects.create(author=user, parent=parent, **validated_data)

        # Add tagged accounts to the post
        if tagged_accounts:
            tagged_users = Account.objects.filter(username__in=tagged_accounts)
            post.tagged_accounts.add(*tagged_users)

        # Handle files and attach them to the post (assuming you have a PostImage model)
        if files:
            for file in files:
                try:
                    hash = get_image_hash(file)
                    image_url = upload_image(
                        file=file, request=self.context.get("request"), folder="posts"
                    )
                    new_file = ImageMedia.objects.create(
                        post=post, image_url=image_url, image_hash=hash
                    )
                    new_file.save()
                except Exception:
                    raise serializers.ValidationError(
                        "An error occurred while uploading the image."
                    )

        return post

    def save(self, **kwargs):
        validated_data = self.validated_data
        return self.create(validated_data)


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = [
            "id",
            "rating",
            "feedback",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]
