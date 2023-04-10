from rest_framework import serializers
from .models import Bookmark
from users.serializers import UserNickSearchSerializer
        
class BookmarkSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Bookmark
        fields = '__all__'  
        
class BookmarksSerializer(serializers.ModelSerializer):
    target = UserNickSearchSerializer()
    class Meta:
        model = Bookmark
        fields = ('id', 'target',)
