from django.contrib import admin
from .models import Message, Spam

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):  
    list_display = ('id', 'sender', 'receiver', 'flavor', 'is_anonymous', 'content', 'is_success', 'is_read', 'sender_deleted', 'receiver_deleted','is_spam','created_at',)
    list_filter = ('sender', 'receiver', 'is_success', 'is_read', 'sender_deleted', 'receiver_deleted','is_spam', )
    search_fields = ('id', 'sender', 'receiver',)
    
@admin.register(Spam)
class SpamAdmin(admin.ModelAdmin):  
    list_display = ('id', 'message', 'is_checked',)
    list_filter = ('is_checked',)
