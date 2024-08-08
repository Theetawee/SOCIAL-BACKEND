from rest_framework import generics

from .models import Post
from .serializers import PostSerializer


class PostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


post_list = PostList.as_view()
