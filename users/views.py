from . import serializers
import requests
from .models import User, TemporalNickname, BannedUser, SiteInfo, PreferenceInfo
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework import exceptions, decorators, permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt import views as jwt_views, serializers as jwt_serializers, exceptions as jwt_exceptions
from config import settings
from django.utils import timezone
from django.http import Http404
from django.contrib.auth import authenticate
from datetime import datetime, timedelta
from myflavors.serializers import MyflavorSerializer
from flavors.serializers import FlavorSerializer
from django.db import transaction
from myflavors.models import Myflavor
from flavors.models import Flavor
from django.core.cache import cache


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
        'redirection_uri': settings.KAKAO_REDIRECT_URL,
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
        # kakao_id, kakao_age, kakao_gender = 3736378603, None, None        
        banned_user = cache.get('banned_user')
        if banned_user is None:
            banned_user = [user.username for user in BannedUser.objects.all()]
            cache.set('banned_user', banned_user, None)
            
        if '1'+str(kakao_id) in banned_user:
            return Response(data={'error' : '가입금지유저'}, status=status.HTTP_403_FORBIDDEN)
                                            
        try:
            user = User.objects.get(username='1'+str(kakao_id))
            
            if user.is_active == True:
                now = datetime.now().strftime('%Y-%m-%d')
                if SiteInfo.objects.filter(created_at__contains = now).exists():
                    today_data = SiteInfo.objects.latest('id')
                    today_data.today_visit_user += 1
                    if user.last_login[:10] != now:
                        today_data.today_user += 1
                    today_data.save()
                else:
                    try:
                        latest_data = SiteInfo.objects.latest('id')
                        SiteInfo.objects.create(today_user=1, today_visit_user=1, current_user=latest_data.current_user, total_user=latest_data.total_user)
                    except SiteInfo.DoesNotExist:
                        number_user = User.objects.all().count()
                        SiteInfo.objects.create(today_user=1, today_visit_user=1, current_user=number_user, total_user=number_user)
                
                user.last_login = timezone.localtime()
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
            
            age_ref = ['None', '10~19','20~29','30~39','40~49','50~59','60~69','70~79']
            gender_ref = ['None','male','female']
            age_ref_index = [i for i, el in enumerate(age_ref) if el == str(kakao_age)][0]
            gender_ref_index = [i for i, el in enumerate(gender_ref) if el == str(kakao_gender)][0]
            try:
                latest_data = PreferenceInfo.objects.latest('id')
                db_age = latest_data.age.split(',')
                db_gender = latest_data.gender.split(',')
                
                new_db_age = []
                for i, age_num in enumerate(db_age):
                    if i == age_ref_index:
                        new_db_age.append(str(int(age_num)+1))
                    else:
                        new_db_age.append(age_num)
                age_result = ','.join(new_db_age)
                
                new_db_gender = []
                for i, gender_num in enumerate(db_gender):
                    if i == gender_ref_index:
                        new_db_gender.append(str(int(gender_num)+1))
                    else:
                        new_db_gender.append(gender_num)
                gender_result = ','.join(new_db_gender)
                
                latest_data.age = age_result
                latest_data.gender = gender_result             
                latest_data.save()
               
            except PreferenceInfo.DoesNotExist:
                PreferenceInfo.objects.create(flavor='0,0,0,0,0,0', flavor_num='0,0,0,0,0,0', age="0,0,0,0,0,0,0,0", gender="0,0,0")
            
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
            
            flavors = [int(flavor) for flavor in request.data['flavor'].split(',')]
            copy_data = request.data.copy()
            copy_data['user'] = user_id
            
            for flavor in flavors:
                copy_data['flavor'] = flavor              
                myflavor_serializer = MyflavorSerializer(data=copy_data)
                myflavor_serializer.is_valid(raise_exception=True)
                myflavor_serializer.save()
            cache.set(f'flavors_{user_id}', flavors, 60*60*24*7*5)    
            user.is_active = True            
            user.last_login = timezone.localtime()
            user.save()
            
            try:
                latest_data = PreferenceInfo.objects.latest('id')
                db_flavor = latest_data.flavor.split(',')
                db_flavor_num = latest_data.flavor_num.split(',')
                
                new_flavor = []
                for i, el in enumerate(db_flavor):
                    if i+1 in flavors:
                        new_flavor.append(str(int(el)+1))
                    else:
                        new_flavor.append(el)
                flavor_result = ','.join(new_flavor)
                
                new_flavor_num = []
                this_flavor_num = len(flavors)
                for i, el in enumerate(db_flavor_num):
                    if i+1 == this_flavor_num:
                        new_flavor_num.append(str(int(el)+1))
                    else:
                        new_flavor_num.append(el)
                flavor_num_result = ','.join(new_flavor_num)
                
                latest_data.flavor = flavor_result
                latest_data.flavor_num = flavor_num_result
                latest_data.save()
                
            except PreferenceInfo.DoesNotExist:
                PreferenceInfo.objects.create(flavor='0,0,0,0,0,0', flavor_num='0,0,0,0,0,0', age="0,0,0,0,0,0,0,0", gender="0,0,0")
         
            now = datetime.now().strftime('%Y-%m-%d')
            if SiteInfo.objects.filter(created_at__contains = now).exists():
                today_data = SiteInfo.objects.latest('id')
                today_data.today_user += 1
                today_data.today_visit_user += 1
                today_data.today_register_user += 1
                today_data.current_user += 1
                today_data.total_user += 1
                today_data.save()
            else:
                try:
                    latest_data = SiteInfo.objects.latest('id')
                    SiteInfo.objects.create(today_user=1, today_visit_user=1, today_register_user=1, current_user=latest_data.current_user+1, total_user=latest_data.total_user+1)
                except SiteInfo.DoesNotExist:
                    number_user = User.objects.all().count()
                    SiteInfo.objects.create(today_user=1, today_visit_user=1, today_register_user=1, current_user=number_user, total_user=number_user)
            return login(user)  
         
@decorators.permission_classes([permissions.IsAuthenticated])
class NicknameSearchView(APIView) :
    def post(self, request):
        user_id = request.user.id
        
        if not 'nickname' in request.data:
            return Response(data={'error' : 'nickname is required'}, status=status.HTTP_400_BAD_REQUEST) 

        users = User.objects.filter(nickname__contains = request.data['nickname'], is_active=True).exclude(is_staff = True).exclude(id=user_id) 
        serializer = serializers.UserNickSearchSerializer(users, many=True)
        
        if request.data["nickname"] == "":
            return Response(data=[], status=status.HTTP_200_OK)
        
        return Response(data=serializer.data, status=status.HTTP_200_OK) 
        
           
class CookieTokenRefreshSerializer(jwt_serializers.TokenRefreshSerializer):
    
    refresh = None

    def validate(self, attrs):
        attrs['refresh'] = self.context['request'].COOKIES.get('refresh')
        if attrs['refresh']:
            return super().validate(attrs)
        else:
            raise jwt_exceptions.InvalidToken(
                'No valid token found in cookie \'refresh\'')


class CookieTokenRefreshView(jwt_views.TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        
        return super().finalize_response(request, response, *args, **kwargs)
    
    
                   
@decorators.permission_classes([permissions.IsAuthenticated])
class LogoutView(APIView):
    def post(self, request):
        try:
            
            refreshToken = request.COOKIES.get('refresh')
            
            token = RefreshToken(refreshToken)
            token.blacklist()
            res = Response()
            res.delete_cookie(
                key = settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                domain=settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN']
                )
            res.delete_cookie("X-CSRFToken")
            res.delete_cookie("csrftoken")
            # res["X-CSRFToken"]=None
            res.data = {"Success" : "Logout successfully"}
                        
            return res
        except:
            raise exceptions.ParseError("Invalid token")
        
        
@decorators.permission_classes([permissions.IsAuthenticated])
class DeleteAccountView(APIView):
    def post(self, request):
        try:
            with transaction.atomic():
                user_id = request.user.id
                # user_id = 9
                user = User.objects.get(id = user_id)
                
                if user.yellow_card == 3:
                    BannedUser.objects.create(username = user.username)
                    
                user.delete()
                
                now = datetime.now().strftime('%Y-%m-%d')
                
                
                if SiteInfo.objects.filter(created_at__contains = now).exists():
                    today_data = SiteInfo.objects.latest('id')
                    today_data.current_user -= 1
                    today_data.today_drop_user += 1
                    today_data.save()
                else:
                    try:
                        latest_data = SiteInfo.objects.latest('id')
                        SiteInfo.objects.create(today_user=1, today_visit_user=1, today_drop_user=1, current_user=latest_data.current_user-1, total_user=latest_data.total_user)
                    except SiteInfo.DoesNotExist:
                        number_user = User.objects.all().count()
                        SiteInfo.objects.create(today_user=1, today_visit_user=1, today_drop_user=1, current_user=number_user, total_user=number_user)
                
       
                #캐시삭제
                try:
                    cache.delete(f'sender_msg_{user_id}')
                    cache.delete(f'receiver_msg_{user_id}')
                    cache.delete(f'flavors_{user_id}')
                    cache.delete(f'change_flavor_{user_id}')
                    cache.delete(f'bookmarks_{user_id}')
                except:
                    pass
                
                refreshToken = request.COOKIES.get('refresh')
                
                token = RefreshToken(refreshToken)
                token.blacklist()
                res = Response()
                res.delete_cookie(
                    key = settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                    domain=settings.SIMPLE_JWT['AUTH_COOKIE_DOMAIN']
                    )
                res.delete_cookie("X-CSRFToken")
                res.delete_cookie("csrftoken")
                # res["X-CSRFToken"]=None
                res.data = {"Success" : "Signout successfully"}
                            
                return res
        except:
            raise exceptions.ParseError("Invalid token")
  
@decorators.permission_classes([permissions.IsAuthenticated])                
class EditNicknameView(APIView):
    def get(self, request):
        try:
            user_id = request.user.id
            user = User.objects.get(id = user_id)
            serializer = serializers.UserNicknameSerializer(user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(data={'error':'this user does not exist'}, status=status.HTTP_404_NOT_FOUND)

        
    def patch(self, request):
        
        try: 
            if not "nickname" in request.data:
                return Response(data={'error':'nickname is required'}, status=status.HTTP_400_BAD_REQUEST)
            user_id = request.user.id
            user = User.objects.get(id = user_id)
            if user.is_changable == False:
                return Response(data={'error':'nickname was already changed'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if user.nickname == request.data["nickname"]:
                return Response(data={'message':'변경사항이 없습니다'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                
            copy_data = request.data.copy()
            copy_data["is_changable"] = False
            serializer = serializers.UserEditNicknameSerializer(user, copy_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK) 
            
        except User.DoesNotExist:
            return Response(data={'error':'this user does not exist'}, status=status.HTTP_404_NOT_FOUND)

@decorators.permission_classes([permissions.IsAuthenticated])                
class MyflavorView(APIView):   
    def get(self, request):
        user_id = request.user.id   
        my_flavors = cache.get(f'flavors_{user_id}')
        if my_flavors is None:
            user = User.objects.get(id = user_id)
            my_flavors = [myflavor.flavor_id for myflavor in user.myflavor.all()]
            cache.set(f'flavors_{user_id}', my_flavors, 60*60*24*7*5) 
                        
        total_flavors = cache.get('total_flavors')
        if total_flavors is None:
            flavors = Flavor.objects.all()
            serializer = FlavorSerializer(flavors, many=True)
            total_flavors = serializer.data
            cache.set('total_flavors', serializer.data, None)   
           
        my_flavors = [flavor for flavor in total_flavors if flavor['id'] in my_flavors]    
        return Response(data=my_flavors, status=status.HTTP_200_OK)   

@decorators.permission_classes([permissions.IsAuthenticated])                
class EditMyflavorView(APIView):   
    def get(self, request):
        user_id = request.user.id
        after_one_week = cache.get(f'change_flavor_{user_id}')
        
        if after_one_week is None:        
            last_edit = Myflavor.objects.filter(user = user_id).last().created_at
            after_one_week = last_edit + timedelta(weeks=1)
            cache.set(f'change_flavor_{user_id}', after_one_week, 60*60*24*7*5) 
        now = datetime.now()
        if now.strftime('%Y-%m-%d') < after_one_week.strftime('%Y-%m-%d'):
            return Response(data={'message': f"{after_one_week.strftime('%Y-%m-%d')}"}, status=status.HTTP_406_NOT_ACCEPTABLE)  
        
        return Response(status=status.HTTP_200_OK)       
    
    def post(self, request):
        if not 'flavor' in request.data:
            return Response(data={'error':'flavor is required'}, status=status.HTTP_400_BAD_REQUEST)
        user_id = request.user.id 
        flavors = [int(flavor) for flavor in request.data['flavor'].split(',')]     
      
        copy_data = request.data.copy()
        copy_data['user'] = user_id   
        with transaction.atomic():
            for flavor in Myflavor.objects.filter(user = user_id):
                flavor.delete()
            for flavor in flavors:
                copy_data['flavor'] = flavor
                myflavor_serializer = MyflavorSerializer(data=copy_data)
                myflavor_serializer.is_valid(raise_exception=True)
                myflavor_serializer.save()
            cache.set(f'flavors_{user_id}', flavors, 60*60*24*7*5)    
            cache.set(f'change_flavor_{user_id}', datetime.now()+ timedelta(weeks=1), 60*60*24*7*5) 
            serializer = MyflavorSerializer(Myflavor.objects.filter(user = user_id), many=True)
            
            try:
                latest_data = PreferenceInfo.objects.latest('id')
                db_flavor = latest_data.flavor.split(',')
                db_flavor_num = latest_data.flavor_num.split(',')
                
                new_flavor = []
                for i, el in enumerate(db_flavor):
                    if i+1 in flavors:
                        new_flavor.append(str(int(el)+1))
                    else:
                        new_flavor.append(el)
                flavor_result = ','.join(new_flavor)
                
                new_flavor_num = []
                this_flavor_num = len(flavors)
                for i, el in enumerate(db_flavor_num):
                    if i+1 == this_flavor_num:
                        new_flavor_num.append(str(int(el)+1))
                    else:
                        new_flavor_num.append(el)
                flavor_num_result = ','.join(new_flavor_num)
                
                latest_data.flavor = flavor_result
                latest_data.flavor_num = flavor_num_result
                latest_data.save()
                
            except PreferenceInfo.DoesNotExist:
                PreferenceInfo.objects.create(flavor='0,0,0,0,0,0', flavor_num='0,0,0,0,0,0', age="0,0,0,0,0,0,0,0", gender="0,0,0")
            
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        
@decorators.permission_classes([permissions.IsAuthenticated])                
class UserUuidView(APIView):   
    def get(self, request):
        user_id = request.user.id 
        user = User.objects.get(id=user_id)
        serializer = serializers.UserInfoSerializer(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
                   
             
            
            
            
            
 

