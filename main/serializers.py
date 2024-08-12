from rest_framework import serializers

from accounts.serializers import BasicAccountSerializer

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author = BasicAccountSerializer(read_only=True)
    comments = serializers.SerializerMethodField()

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
        ]

    def get_comments(self, obj):
        return Post.objects.filter(parent=obj).count()


class CreatePostSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)

    def create(self, validated_data):
        user = self.context["request"].user
        parent_id = self.context.get("post_id")
        parent = None
        if parent_id:
            try:
                parent = Post.objects.get(id=parent_id)
            except Exception as e:
                raise serializers.ValidationError(str(e))
        post = Post.objects.create(author=user, **validated_data, parent=parent)
        return post

    def save(self, **kwargs):
        validated_data = self.validated_data
        return self.create(validated_data)
