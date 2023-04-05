from django.contrib import admin
from .models import Myflavor

@admin.register(Myflavor)
class FlavorAdmin(admin.ModelAdmin):  
    list_display = ('id', 'user', 'flavor', 'created_at')
