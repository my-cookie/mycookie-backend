from django.urls import path
from . import views



urlpatterns = [
    path('login',views.KakaoLoginView.as_view()),
    path('info',views.UserInfoRegisterView.as_view()),
    path('nickname', views.NicknameConfirm.as_view()),
    path('search', views.NicknameSearchView.as_view()),
    path('access', views.CookieTokenRefreshView.as_view()),
    path('nickname/edit', views.EditNicknameView.as_view()),
    path('myflavor/edit', views.EditMyflavorView.as_view()),
    path('myflavor', views.MyflavorView.as_view()),
]