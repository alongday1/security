from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from forum.models import Post, GroupPost
from .serializers import PostSerializer, GroupPostSerializer
from rest_framework import status
from django.db.models import Q

class PostListView(APIView):
    def get(self, request):
        posts = Post.objects.all()
        group_posts = GroupPost.objects.all()
        post_serializer = PostSerializer(posts, many=True)
        group_post_serializer = GroupPostSerializer(group_posts, many=True)

        return Response({
            'posts': post_serializer.data,
            'group_posts': group_post_serializer.data
        })

class SearchPostView(APIView):
    def get(self, request):
        query = request.GET.get('q', '')
        if query:
            posts = Post.objects.filter(Q(title__icontains=query) | Q(author__username__icontains=query))
            group_posts = GroupPost.objects.filter(Q(title__icontains=query) | Q(sponser__username__icontains=query))
        else:
            posts = Post.objects.none()
            group_posts = GroupPost.objects.none()

        post_serializer = PostSerializer(posts, many=True)
        group_post_serializer = GroupPostSerializer(group_posts, many=True)

        return Response({
            'posts': post_serializer.data,
            'group_posts': group_post_serializer.data
        }, status=status.HTTP_200_OK)