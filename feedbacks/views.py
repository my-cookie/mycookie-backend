from . import serializers
from .models import Feedback
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework import exceptions, decorators, permissions, status
from datetime import datetime
from django.db import transaction
from django.core.cache import cache


class FeedbackView(APIView) :

    def post(self, request):
        user_id = 7
        copy_data = request.data.copy()
        copy_data['user'] = user_id
        serializer = serializers.FeedbackSerializer(data = copy_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(data=serializer.data, status=status.HTTP_200_OK)
