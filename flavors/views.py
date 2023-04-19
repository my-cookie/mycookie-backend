from . import serializers
from .models import Flavor
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework import exceptions, decorators, permissions, status
from datetime import datetime
from django.db import transaction
from django.core.cache import cache


class FlavorsView(APIView) :

    def get(self, request):
        
        total_flavors = cache.get('total_flavors')
        if total_flavors is None:
            flavors = Flavor.objects.all()
            serializer = serializers.FlavorSerializer(flavors, many=True)
            total_flavors = serializer.data
            cache.set('total_flavors', total_flavors, None)        
        
        return Response(data=total_flavors, status=status.HTTP_200_OK)
        
        
