from django.db import models

class Feedback(models.Model):  
    choice = (
    	('E', '오류'),
        ('U', '불편사항'),
        ('R', '건의사항'),
        ('C', '칭찬'),
    ) 
    user = models.ForeignKey('users.User', on_delete=models.SET_DEFAULT, default=11)
    title = models.CharField(max_length=10, choices=choice)
    content = models.CharField(max_length=255, blank=False, null=False)
    is_checked = models.BooleanField(default=False, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __str__(self):
        return self.title