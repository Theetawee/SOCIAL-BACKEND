from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Post
from .serializers import CreatePostSerializer, PostSerializer


class PostList(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        posts = Post.objects.filter(parent=None)
        return posts

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


post_list = PostList.as_view()


class PostDetail(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


post_detail = PostDetail.as_view()


class PostCommentsList(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        post_id = self.kwargs.get("pk")
        parent_post = Post.objects.get(id=post_id)
        posts = Post.objects.filter(parent=parent_post)

        return posts


comment_list = PostCommentsList.as_view()


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_post(request, post_id=None):
    serializer = CreatePostSerializer(
        data=request.data, context={"request": request, "post_id": post_id}
    )

    if serializer.is_valid():
        post = serializer.save()
        return Response(
            PostSerializer(post, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_action(request, action, post_id):
    user = request.user
    try:
        post = Post.objects.get(id=post_id)
    except Exception as e:
        return Response(str(e), status=status.HTTP_404_NOT_FOUND)
    if action == "like":
        if user in post.likes.all():
            post.likes.remove(user)
        else:
            post.likes.add(user)
        post.save()
    else:
        return Response(
            {"msg": "No action provided"}, status=status.HTTP_400_BAD_REQUEST
        )

    return Response({"msg": "Updated"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def register_post_view(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        post.views += 1
        post.save()
        return Response({"msg": "success"}, status=status.HTTP_200_OK)
    except Exception:
        return Response({"msg": "error"}, status=status.HTTP_400_BAD_REQUEST)
