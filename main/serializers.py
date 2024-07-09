from rest_framework import serializers
from .models import Article, Category
from taggit.serializers import TagListSerializerField, TaggitSerializer
from accounts.serializers import BasicAccountSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ArticleSerializer(serializers.ModelSerializer, TaggitSerializer):
    category = CategorySerializer()
    tags = TagListSerializerField()
    author = BasicAccountSerializer()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "summary",
            "image",
            "featured",
            "created_at",
            "updated_at",
            "slug",
            "category",
            "author",
            "tags",
            "image_hash",
            "image_alt"
        ]
