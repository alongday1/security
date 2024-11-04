from forum.models import Post, GroupPost,Forum
from rest_framework import serializers
from django.contrib.auth.models import User

class ForumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = ['name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class PostSerializer(serializers.ModelSerializer):
    forum_name = serializers.CharField(source='forum.name', read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'forum_name','author_name']

class GroupPostSerializer(serializers.ModelSerializer):
    sponser_name = serializers.CharField(source='sponser.username', read_only=True)

    class Meta:
        model = GroupPost
        fields = ['id', 'title', 'sponser_name'] 