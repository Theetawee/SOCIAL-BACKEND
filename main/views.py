from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view
from .serializers import ArticleSerializer
from .models import Article
from django.core.exceptions import ObjectDoesNotExist


@api_view(["GET"])
def homepage(request):
    try:
        main_article = Article.objects.filter(featured=True).latest("created_at")
    except ObjectDoesNotExist:
        main_article = None

    featured_articles = Article.objects.filter(featured=True).exclude(
        id=main_article.id if main_article else None
    )[:3]
    articles = Article.objects.filter(featured=False)[:4]

    main_article_serializer = ArticleSerializer(main_article) if main_article else None
    featured_articles_serializer = ArticleSerializer(featured_articles, many=True)
    articles_serializer = ArticleSerializer(articles, many=True)

    response = {
        "main_article": (
            main_article_serializer.data if main_article_serializer else None
        ),
        "featured_articles": featured_articles_serializer.data,
        "articles": articles_serializer.data,
    }

    return Response(status=status.HTTP_200_OK, data=response)


class ArticleDetail(generics.RetrieveAPIView):
    serializer_class = ArticleSerializer
    queryset = Article.objects.all()
    lookup_field = "slug"
