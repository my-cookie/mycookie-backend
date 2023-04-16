from rest_framework import serializers
from .models import Message, Spam
from users.serializers import UserNicknameSerializer
from flavors.serializers import FlavorImgSerializer

class MessageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Message
        fields = '__all__' 
         
class SpamSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Spam
        fields = '__all__'  
        
class ReadMessageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Message
        fields = ('is_read',)
        
class SpamMessageSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Message
        fields = ('is_spam',)
        
class SenderMsgSerializer(serializers.ModelSerializer):
    sender = UserNicknameSerializer()
    receiver = UserNicknameSerializer()
    flavor = FlavorImgSerializer()
    
    class Meta:
        model = Message
        fields = ('id', 'sender', 'receiver', 'flavor', 'is_anonymous', 'content','is_read','created_at',)   
        
class ReceiverMsgSerializer(serializers.ModelSerializer):
    sender = UserNicknameSerializer()
    receiver = UserNicknameSerializer()
    flavor = FlavorImgSerializer()
    class Meta:
        model = Message
        fields = ('id', 'sender', 'receiver', 'flavor', 'is_anonymous', 'content','is_spam','created_at',)
        
