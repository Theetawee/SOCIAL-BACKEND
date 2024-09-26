from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Account
from accounts.serializers import BasicAccountSerializer

from .models import ImageMedia, Post
from .serializers import CreatePostSerializer, FeedbackSerializer, PostSerializer
from .utils import delete_images_from_cloudinary


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


@api_view(["GET"])
def search_view(request):
    search_term = request.GET.get("q")

    if search_term:
        # Search in Post model for content containing the search term
        post_results = Post.objects.filter(Q(content__icontains=search_term))

        # Search in Account model for username or name containing the search term
        account_results = Account.objects.filter(
            Q(username__icontains=search_term) | Q(name__icontains=search_term)
        )

        # Serialize the results (assume you have PostSerializer and AccountSerializer)
        post_serializer = PostSerializer(post_results, many=True)
        account_serializer = BasicAccountSerializer(account_results, many=True)

        return Response(
            {"posts": post_serializer.data, "accounts": account_serializer.data},
            status=status.HTTP_200_OK,
        )

    return Response(
        {"error": "No search term provided."}, status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["POST"])
def get_feedback(request):
    serializer = FeedbackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_action(request, post_id):
    # Get the post or return a 404 response if not found
    post = get_object_or_404(Post, id=post_id)

    # Check if the user is the owner of the post
    if post.author != request.user:
        return Response(
            {"detail": "You do not have permission to delete this post."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Get associated images from the ImageMedia model
    images = ImageMedia.objects.filter(post=post)
    image_urls = [image.image_url for image in images]

    # Call the function to delete images from Cloudinary concurrently
    delete_images_from_cloudinary(image_urls)

    # Delete the post and associated images from the database
    images.delete()
    post.delete()

    return Response(
        {"detail": "Post and associated images deleted successfully."},
        status=status.HTTP_204_NO_CONTENT,
    )
