from django.db import models


class Message(models.Model):   
    
    receiver = models.ForeignKey('users.User', related_name='receiver', on_delete=models.SET_DEFAULT, default=11)
    sender = models.ForeignKey('users.User', related_name='sender', on_delete=models.SET_DEFAULT, default=11)
    flavor = models.ForeignKey('flavors.Flavor', on_delete=models.PROTECT)
    is_anonymous = models.BooleanField(blank=False, null=False)
    content = models.CharField(max_length=255, blank=False, null=False)
    is_success = models.BooleanField(default=False, blank=True, null=False)
    is_read = models.BooleanField(default=False, blank=True, null=False)
    sender_deleted = models.BooleanField(default=False, blank=True, null=False)
    receiver_deleted = models.BooleanField(default=False, blank=True, null=False)
    sender_canceled = models.BooleanField(default=False, blank=True, null=False)
    is_spam = models.BooleanField(default=False, blank=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return f'{self.sender}-{self.receiver}'
    
    class Meta:
        ordering = ['-id']
    
class Spam(models.Model):
    message = models.ForeignKey('msgs.Message', on_delete=models.CASCADE)
    is_checked = models.BooleanField(default=False, null=False, blank=False) 

