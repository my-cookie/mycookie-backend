from rest_framework import serializers
from .models import User, TemporalNickname, SiteInfo



        
class KakaoSerializer(serializers.Serializer):
    code = serializers.CharField() 
    
# class UserRegisterValidationSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = User
#         exclude = ('password','username')

class UserRegisterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        exclude = ('password',)
        
class UserInfoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('uuid','nickname',)
        
class UserNicknameSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('nickname',)
        
class UserNickSearchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id','nickname',)
        
class NicknameConfirmSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TemporalNickname
        fields = '__all__'
        
class UserEditNicknameSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('nickname', 'is_changable')
        
class RealtimeUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SiteInfo
        fields = ('realtime_user',)
        
