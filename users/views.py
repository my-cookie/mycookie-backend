from . import serializers
import requests
from .models import User, TemporalNickname
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework import exceptions, decorators, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt import views as jwt_views, serializers as jwt_serializers, exceptions as jwt_exceptions
from config import settings
from django.utils import timezone
from django.http import Http404
from django.contrib.auth import authenticate
from datetime import datetime
from myflavors.serializers import MyflavorSerializer
from django.db import transaction

def get_tokens_for_user(user):
    
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
def login(user):

    tokens = get_tokens_for_user(user)
    res = Response()
    serializer = serializers.UserInfoSerializer(user)
    res.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE'],
        value=tokens["access"],
        expires=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        domain=settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
        )
    res.set_cookie(
        key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
        value=tokens["refresh"],
        expires=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
        domain=settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN'],
        secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
        httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
        samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
    )
    res.data = {"Success" : "Login successfully","tokens":tokens, "user":serializer.data}  
    
    res.status=status.HTTP_200_OK
    
    return res

def kakao_access(request):
    serializer = serializers.KakaoSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    auth_code = serializer.validated_data["code"]
    
    kakao_token_api = 'https://kauth.kakao.com/oauth/token'
    data = {
        'grant_type': 'authorization_code',
        'client_id': settings.KAKAO_REST_API_KEY,
        'redirection_uri': 'http://localhost:3000/oauth/callback/kakao',
        'code': auth_code
    }

    token_response = requests.post(kakao_token_api, data=data).json()
    if token_response.get('error'):
        raise Http404
    
    access_token = token_response.get('access_token')
   

    user_info_response = requests.get('https://kapi.kakao.com/v2/user/me', headers={"Authorization": f'Bearer ${access_token}'})
    
    kakao_id = user_info_response.json()['id']
    try:
        kakao_age = user_info_response.json()['kakao_account']['age_range']
    except:
        kakao_age = None
    try:
        kakao_gender = user_info_response.json()['kakao_account']['gender']
    except:
        kakao_gender = None
    
    return kakao_id, kakao_age, kakao_gender


class KakaoLoginView(APIView) :
    
    def post(self, request):
                    
        kakao_id, kakao_age, kakao_gender = kakao_access(request)  
                                            
        try:
            User.objects.get(username='1'+str(kakao_id))
            user = User.objects.get(username='1'+str(kakao_id))
            
            if user.is_active == True:
                user.last_login = timezone.now()
                user.save()
                return login(user) 
            elif user.yellow_card >= 3:
                return Response(data={'error' : 'banned user'}, status=status.HTTP_400_BAD_REQUEST)
                # 정지된 유저이다.
            else:
                return Response(data={'error': 'non-info user','user_uuid':user.uuid}, status=status.HTTP_206_PARTIAL_CONTENT)
                # 등록된 유저인데 inactive 상태이면 프론트에서 정보입력 페이지로 가야한다.
            
        except User.DoesNotExist: 
              
            request_data_copy = request.data.copy()  
            request_data_copy['username'] = '1'+str(kakao_id)          
            request_data_copy['nickname'] = '1'+str(kakao_id)                 
            request_data_copy['age'] = str(kakao_age)                 
            request_data_copy['gender'] = str(kakao_gender)                 
            serializer = serializers.UserRegisterSerializer(data=request_data_copy)
            
            serializer.is_valid(raise_exception=True)
            serializer.save() 
            
            return Response(data={'user_uuid':serializer.data['uuid']}, status=status.HTTP_201_CREATED)
            # 새로운 유저는 프론트에서 정보입력 페이지로 가야한다.

class NicknameConfirm(APIView) :
    def post(self, request):
        if not 'user_uuid' in request.data:
            return Response(data={'error':"user_uuid is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(uuid=request.data['user_uuid'])
        except:
            return Response(data={'error':"This user does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        user.temp.all().delete()
        copy_data = request.data.copy()
        copy_data['user'] = user.id
        serializer = serializers.NicknameConfirmSerializer(data=copy_data)
        serializer.is_valid(raise_exception=True)
        
        if '사라진쿠키' in request.data['nickname']:
            return Response(data={'error':'someone already got this nickname'}, status=status.HTTP_206_PARTIAL_CONTENT)
        
        if TemporalNickname.objects.filter(nickname = request.data['nickname']).exists():
            return Response(data={'error':'someone already got this nickname'}, status=status.HTTP_206_PARTIAL_CONTENT)
        elif User.objects.filter(nickname = request.data['nickname']).exists(): 
            return Response(data={'error':'someone already got this nickname'}, status=status.HTTP_206_PARTIAL_CONTENT)
        else:
            serializer.save()
            return Response(data={'success':'This nickname is usable'}, status=status.HTTP_200_OK)         
             
class UserInfoRegisterView(APIView) :
    #flavor는 다중 선택이 가능하므로 ,로 구분된 문자열을 받는다.
    def post(self, request):                         

        if not 'user_uuid' in request.data or not 'flavor' in request.data or not 'nickname' in request.data:
            return Response(data={'error' : 'user_uuid, flavor, nickname are required'}, status=status.HTTP_400_BAD_REQUEST) 
        
        try:
            user = User.objects.get(uuid=request.data['user_uuid'])
        except:
            return Response(data={'error':"This user does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
        user_id = user.id
        nickname_serializer = serializers.UserNicknameSerializer(user, data=request.data, partial = True)
        nickname_serializer.is_valid(raise_exception=True)
        
        try:
            TemporalNickname.objects.get(nickname = request.data['nickname']).delete()
        except TemporalNickname.DoesNotExist:
            return Response(data={'error' : '닉네임 중복 검사 필요'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        with transaction.atomic():
            nickname_serializer.save()
            
            flavors = request.data['flavor'].split(',')
            copy_data = request.data.copy()
            copy_data['user'] = user_id
            
            for flavor in flavors:
                copy_data['flavor'] = flavor
                myflavor_serializer = MyflavorSerializer(data=copy_data)
                myflavor_serializer.is_valid(raise_exception=True)
                myflavor_serializer.save()
                
            user.is_active = True            
            user.last_login = timezone.now()
            user.save()
            return login(user)   

class NicknameSearchView(APIView) :
    def post(self, request):
        
        if not 'nickname' in request.data:
            return Response(data={'error' : 'nickname is required'}, status=status.HTTP_400_BAD_REQUEST) 

        users = User.objects.filter(nickname__contains = request.data['nickname']) 
        serializer = serializers.UserNickSearchSerializer(users, many=True)
        print(len(serializer.data))
        if len(serializer.data) == 0:
            return Response(data='일치하는 유저가 없어요', status=status.HTTP_206_PARTIAL_CONTENT)
        return Response(data=serializer.data, status=status.HTTP_200_OK) 
        
           
             
             

            
 

