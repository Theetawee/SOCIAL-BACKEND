from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from accounts.models import Account
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Post, ContentImage, Comment

from main.serializers.create.serializers import (
    CreatePostSerializer,
    CreateCommentSerializer,
)
from accounts.serializers.view.serializers import (
    SuggestedAccountsSerializer,
    AccountSerializer,
)
from main.serializers.view.serializers import (
    PostSerializer,
    ContentImageSerializer,
    CommentSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def ping_server(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def create_post(request):
    if request.method == "POST":
        serializer = CreatePostSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(account=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


@api_view(["POST"])
def create_comment(request):
    if request.method == "POST":
        serializer = CreateCommentSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(account=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
    )


class Posts(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user = self.request.user
        is_admin = user.is_staff
        account_param = self.request.query_params.get("account", None)
        if account_param:
            try:
                account = Account.objects.get(username=account_param)
                if is_admin:
                    return Post.objects.filter(account=account)
                else:
                    queryset = (
                        Post.objects.select_related("account")
                        .prefetch_related("likes")
                        .filter(account=account)
                        .all()
                    )

                return queryset
            except Account.DoesNotExist:
                return Response(
                    {"detail": "Account not found"}, status=status.HTTP_404_NOT_FOUND
                )

        else:
            if is_admin:
                return Post.objects.all()
            else:
                queryset = (
                    Post.objects.select_related("account")
                    .prefetch_related("likes")
                    .all()
                )

                return queryset


posts = Posts.as_view()


@api_view(["POST"])
def like_post(request, pk, type="post"):
    try:
        if type == "post":
            post = get_object_or_404(Post, id=pk)
        elif type == "comment":
            pass
            # post = get_object_or_404(Comment, id=pk)
        else:
            return Response(
                {"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Check if the user has disliked the post
        if request.user in post.dislikes.all():
            post.dislikes.remove(request.user)

        # Toggle liking status
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            return Response(
                {"is_liked": False, "total_likes": post.total_likes},
                status=status.HTTP_201_CREATED,
            )
        else:
            post.likes.add(request.user)
            return Response(
                {"is_liked": True, "total_likes": post.total_likes},
                status=status.HTTP_201_CREATED,
            )

    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["POST"])
def dislike_post(request, pk, type="post"):
    try:
        if type == "post":
            post = get_object_or_404(Post, id=pk)
        elif type == "comment":
            pass
            # post = get_object_or_404(Comment, id=pk)
        else:
            return Response(
                {"error": "Invalid type"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user has disliked the post
        if request.user in post.likes.all():
            post.likes.remove(request.user)

        # Toggle liking status
        if request.user in post.dislikes.all():
            post.dislikes.remove(request.user)
        else:
            post.dislikes.add(request.user)

        return Response({"dislike": "success"}, status=status.HTTP_201_CREATED)

    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)


class PostDetail(generics.RetrieveAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):

        # Filter posts based on privacy settings
        queryset = (
            Post.objects.select_related("account").prefetch_related("likes")
        ).all()

        return queryset


post_detail = PostDetail.as_view()


@api_view(["GET"])
def get_post_image(request, pk):
    try:
        post = get_object_or_404(Post, id=pk)
        images = ContentImage.objects.filter(post=post)
        serializer = ContentImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
def get_accounts_to_tag(request):
    account = request.GET.get("account", None)
    if account:
        accounts = Account.objects.filter(username__icontains=account).exclude(
            id=request.user.id
        )
        serializer = SuggestedAccountsSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def search(request):
    query = request.GET.get("query")
    if query is None or query.strip() == "":
        return Response(status=status.HTTP_400_BAD_REQUEST)

    accounts = Account.objects.filter(
        Q(username__icontains=query) | Q(name__icontains=query)
    )
    accounts_data = AccountSerializer(accounts, many=True)

    posts = Post.objects.filter(Q(content__icontains=query))

    posts_data = PostSerializer(posts, many=True)

    response = {"accounts": accounts_data.data, "posts": posts_data.data}
    return Response(response, status=status.HTTP_200_OK)


class Comments(generics.ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        postId = self.kwargs.get("pk")
        queryset = Comment.objects.filter(post_id=postId)

        return queryset


comments = Comments.as_view()
