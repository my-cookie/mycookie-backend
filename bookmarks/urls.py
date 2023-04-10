from django.urls import path
from . import views


urlpatterns = [
    path('item',views.BookmarkView.as_view()),
     
]