from django.db import models

# Create your models here.


class Data(models.Model):
    text = models.CharField(max_length=10000000)
