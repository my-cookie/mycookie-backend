from django.urls import path
from . import views


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('login',views.KakaoLoginView.as_view()),
    path('info',views.UserInfoRegisterView.as_view()),
    path('nickname', views.NicknameConfirm.as_view()),
    # path('admin/login', views.StaffLoginView.as_view()),
    # path('guest/register', views.GuestLoginView.as_view()), 
]