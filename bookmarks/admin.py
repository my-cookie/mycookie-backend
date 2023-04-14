from django.contrib import admin
from .models import Bookmark

@admin.register(Bookmark)
class FlavorAdmin(admin.ModelAdmin):  
    list_display = ('id', 'owner', 'target',)
    list_filter = ('owner', 'target',)

