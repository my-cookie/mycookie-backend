from django.urls import path
from . import views

urlpatterns = [
    path('save',views.SendMsgView.as_view()),
    path('read',views.ReadMessageView.as_view()),
    path('remain',views.RemainMsgView.as_view()),
    path('sender',views.SenderMsgView.as_view()),
    path('receiver',views.ReceiverMsgView.as_view()),
     
]