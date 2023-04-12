from . import serializers
from .models import Bookmark
from users.models import User
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework import exceptions, decorators, permissions, status
from datetime import datetime
from django.db import transaction
from django.core.cache import cache


class BookmarkView(APIView) :
    def get(self, request):
        user_id = 7
        bookmarks = Bookmark.objects.filter(owner = user_id)
        serializer = serializers.BookmarksSerializer(bookmarks, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK) 
    
    def post(self, request):
        user_id = 7 
        copy_data = request.data.copy()
        copy_data['owner'] = user_id
        if Bookmark.objects.filter(owner=user_id, target=request.data['target']).exists():
            return Response(data='already exists', status=status.HTTP_206_PARTIAL_CONTENT)
        serializer = serializers.BookmarkSerializer(data = copy_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        new = Bookmark.objects.get(id=serializer.data['id'])
        serializer = serializers.BookmarksSerializer(new)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED) 
    
    def delete(self, request):
        try:
            if not 'target' in request.data:
                return Response(data={'error':'target is required'}, status=status.HTTP_400_BAD_REQUEST) 
            bookmark = Bookmark.objects.get(target=request.data['target'])
            bookmark.delete()
            return Response(data='deleted', status=status.HTTP_200_OK) 
            
        except Bookmark.DoesNotExist:
            return Response(data={'error':'this bookmark does not exist'}, status=status.HTTP_404_NOT_FOUND) 
            
