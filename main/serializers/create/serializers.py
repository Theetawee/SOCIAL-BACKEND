from rest_framework import serializers
import json
from main.models import Post, ContentImage, Comment
from accounts.models import Account


class CreatePostSerializer(serializers.ModelSerializer):
    content = serializers.CharField(style={"base_template": "textarea.html"})
    taged_accounts = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = ["content", "account", "taged_accounts"]

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
            for account in taged_accounts_data:
                account_id = account["id"]
                if account_id:
                    tagged_account = Account.objects.get(id=account_id)
                    post.taged_accounts.add(tagged_account)

        return post


class CreateCommentSerializer(serializers.ModelSerializer):
    content = serializers.CharField(style={"base_template": "textarea.html"})
    taged_accounts = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Comment
        fields = ["content", "account", "taged_accounts", "post"]

    def create(self, validated_data):
        taged_accounts_data = validated_data.pop("taged_accounts", [])
        files = self.context["request"].FILES.getlist("files")

        # Create the post instance
        comment = super(CreateCommentSerializer, self).create(validated_data)

        # Handle the list of images if available
        for file_data in files:
            ContentImage.objects.create(comment=comment, content_image=file_data)

        # Handle tagged accounts
        if taged_accounts_data:
            taged_accounts_data = taged_accounts_data[0]
            taged_accounts_data = json.loads(taged_accounts_data)
            for account in taged_accounts_data:
                account_id = account["id"]
                if account_id:
                    tagged_account = Account.objects.get(id=account_id)
                    comment.taged_accounts.add(tagged_account)

        return comment
