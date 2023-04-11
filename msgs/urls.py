from django.urls import path
from . import views

urlpatterns = [
    path('save',views.SendMsgView.as_view()),
    path('read',views.ReadMessageView.as_view()),
    path('remain',views.RemainMsgView.as_view()),
     
]