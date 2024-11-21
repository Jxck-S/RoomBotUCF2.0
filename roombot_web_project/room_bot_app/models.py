from django.db import models

# Create your models here.
from django.db import models

class Login(models.Model):
    name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100, null=True, blank=True)
    UCFID = models.CharField(max_length=20)
    NID = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    validCredentials = models.BooleanField(default=True)
    updated = models.DateField()
