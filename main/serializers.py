from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from rest_framework import serializers

from accounts.models import Account
from accounts.serializers import BasicAccountSerializer

from .models import Post


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
