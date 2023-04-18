from . import serializers
from .models import Bookmark
from users.models import User
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework import exceptions, decorators, permissions, status
from datetime import datetime
from django.db import transaction
from django.core.cache import cache

@decorators.permission_classes([permissions.IsAuthenticated])
class BookmarkView(APIView) :
    def get(self, request):
        user_id = request.user.id
        
        bookmarks = cache.get(f'bookmarks_{user_id}')
        
        if bookmarks is None:
            bookmarks = Bookmark.objects.filter(owner = user_id)
            bookmarks_serializer = serializers.BookmarksSerializer(bookmarks, many=True)
            bookmarks = bookmarks_serializer.data
            cache.set(f'bookmarks_{user_id}', bookmarks, 60*60*24)  
        
        return Response(data=bookmarks, status=status.HTTP_200_OK) 
    
    def post(self, request):
        
        user_id = request.user.id 
        copy_data = request.data.copy()
        
        bookmarks = cache.get(f'bookmarks_{user_id}')
        
        if bookmarks is None:
            bookmarks = Bookmark.objects.filter(owner = user_id)
            bookmarks_serializer = serializers.BookmarksSerializer(bookmarks, many=True)
            bookmarks = bookmarks_serializer.data
            cache.set(f'bookmarks_{user_id}', bookmarks, 60*60*24)                
                        
        copy_data['owner'] = user_id
        
        if request.data['target'] in [bookmark["target"]["id"] for bookmark in bookmarks]:
            return Response(data='already exists', status=status.HTTP_206_PARTIAL_CONTENT)
        
        serializer = serializers.BookmarkSerializer(data = copy_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        bookmarks = bookmarks_serializer.data.append(serializer.data)
        cache.set(f'bookmarks_{user_id}', bookmarks, 60*60*24)    
        
        return Response(data=serializer.data, status=status.HTTP_201_CREATED) 
    
    def delete(self, request):
        try:
            if not 'target' in request.data:
                return Response(data={'error':'target is required'}, status=status.HTTP_400_BAD_REQUEST) 
            
            user_id = request.user.id
            bookmarks = cache.get(f'bookmarks_{user_id}')
        
            if bookmarks is None:
                bookmarks = Bookmark.objects.filter(owner = user_id)
                bookmarks_serializer = serializers.BookmarksSerializer(bookmarks, many=True)
                bookmarks = bookmarks_serializer.data
                cache.set(f'bookmarks_{user_id}', bookmarks, 60*60*24) 
                   
            with transaction.atomic():
                bookmark_deleted = Bookmark.objects.get(owner = user_id, target=request.data['target'])
                bookmark_deleted.delete()
                bookmarks = [bookmark for bookmark in bookmarks if request.data['target'] != bookmark["target"]["id"]]
                cache.set(f'bookmarks_{user_id}', bookmarks, 60*60*24) 
                return Response(data='deleted', status=status.HTTP_200_OK) 
            
        except Bookmark.DoesNotExist:
            return Response(data={'error':'this bookmark does not exist'}, status=status.HTTP_404_NOT_FOUND) 
            
