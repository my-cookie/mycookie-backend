from django.urls import path
from . import views

urlpatterns = [
    path('save',views.FlavorConfirm.as_view()),
    path('read',views.ReadMessage.as_view()),
     
]