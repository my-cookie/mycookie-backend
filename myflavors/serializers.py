from rest_framework import serializers
from .models import Myflavor

class MyflavorSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Myflavor
        fields = ('user', 'flavor', )  