from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import uuid

class User(AbstractUser):
    nicknameRegex = RegexValidator(regex = r'^([가-힣a-zA-Z0-9]{1,20})$', message='Enter a valid nickname',code=400)
    
    username = models.CharField(max_length=20, unique=True, blank=False, null=False)
    nickname = models.CharField(validators = [nicknameRegex], max_length=20, unique=True, blank=False, null=False)  #프론트에서 length 검사 필요
    age = models.CharField(max_length=10, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=False, blank=True, null=False)
    is_changable = models.BooleanField(default=True, blank=True, null=False)
    yellow_card = models.PositiveIntegerField(default=0, blank=True, null=False)
    uuid = models.UUIDField(default=uuid.uuid4)
    
    def __str__(self):
        return self.nickname
    
    # class Meta:
    #     indexes = [
    #         models.Index(fields=["nickname", "uuid"]),
    #     ]
    
class TemporalNickname(models.Model):
    nicknameRegex = RegexValidator(regex = r'^([가-힣a-zA-Z0-9]{1,20})$', message='Enter a valid nickname',code=400)
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='temp')
    nickname = models.CharField(validators = [nicknameRegex], max_length=20, unique=True, blank=False, null=False)  #프론트에서 length 검사 필요
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

class BannedUser(models.Model):
    username = models.CharField(max_length=20, unique=True, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
class SiteInfo(models.Model):
    today_visit_user = models.PositiveIntegerField(default=0, null=False) #오늘 방문한 유저 수
    today_user = models.PositiveIntegerField(default=0, null=False) #오늘 로그인한 유저 수
    today_register_user = models.PositiveIntegerField(default=0, null=False) #오늘 신규가입자
    today_drop_user = models.PositiveIntegerField(default=0, null=False) #오늘 탈퇴가입자
    today_message = models.PositiveIntegerField(default=0, null=False) #오늘 메시지 전송량
    today_success_message = models.PositiveIntegerField(default=0, null=False) #오늘 메시지 전송량
    realtime_user = models.PositiveIntegerField(default=0, null=False) #현재 소켓 접속자 수
    current_user = models.PositiveIntegerField(default=0, null=False) #현재 가입자 수
    total_user = models.PositiveIntegerField(default=0, null=False) #누적 가입자 수
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    
class PreferenceInfo(models.Model):
    flavor = models.CharField(max_length=255, null=False)
    flavor_num = models.CharField(max_length=255, null=False)
    age = models.CharField(max_length=255, null=False)
    gender = models.CharField(max_length=255, null=False)
    

    
    
    