from django.urls import path
from . import views

urlpatterns = [
    path('save',views.SendMsgView.as_view()),
    path('read',views.ReadMessageView.as_view()),
    path('remain',views.RemainMsgView.as_view()),
    path('sender',views.SenderMsgView.as_view()),
    path('receiver',views.ReceiverMsgView.as_view()),
    path('total',views.TotalMessageView.as_view()),
    path('spam',views.SpamReportView.as_view()),
    path('sender/delete',views.SenderDeleteMsgView.as_view()),
    path('receiver/delete',views.ReceiverDeleteMsgView.as_view()),
    path('sender/cancel',views.SenderCancelMsgView.as_view()),
    path('receiver/alarm',views.SingleReceiverMessageView.as_view()),
     
]