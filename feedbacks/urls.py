from django.urls import path
from . import views


urlpatterns = [
    path('item',views.FeedbackView.as_view()),
     
]