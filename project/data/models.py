from django.db import models

# Create your models here.


class Data(models.Model):
    name = models.CharField(max_length=10000000, blank=True, null=True)
    text = models.CharField(max_length=10000000, blank=True, null=True)
