from rest_framework import serializers
from .models import Flavor

class FlavorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Flavor
        fields = '__all__'  
        
class FlavorImgSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Flavor
        fields = ('img',)
        
