from django.db import models


class Myflavor(models.Model):   
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    flavor = models.ForeignKey('flavors.Flavor', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.user
