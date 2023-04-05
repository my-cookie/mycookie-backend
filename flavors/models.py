from django.db import models


class Flavor(models.Model):   
    
    name = models.CharField(max_length=20, blank=False, null=False)
    img = models.CharField(max_length=255, blank=False, null=False)

    def __str__(self):
        return self.name