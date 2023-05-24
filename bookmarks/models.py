from django.db import models


class Bookmark(models.Model):   
    
    owner = models.ForeignKey('users.User', related_name='bookmark_owner', on_delete=models.CASCADE)
    target = models.ForeignKey('users.User', related_name='bookmark_target', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.owner}'
    
    class Meta:
        ordering = ['-id']
