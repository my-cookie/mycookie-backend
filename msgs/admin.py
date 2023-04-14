from django.contrib import admin
from .models import Message

@admin.register(Message)
class FlavorAdmin(admin.ModelAdmin):  
    list_display = ('id', 'sender', 'receiver', 'flavor', 'is_anonymous', 'content', 'is_success', 'is_read', 'sender_deleted', 'receiver_deleted','is_spam','created_at',)
    list_filter = ('sender', 'receiver', 'is_success', 'is_read', 'sender_deleted', 'receiver_deleted','is_spam', )
