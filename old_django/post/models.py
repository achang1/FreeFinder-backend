from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=50, blank=False, null=False)
    text = models.CharField(max_length=300, blank=False, null=False)
    user = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE, null=False)

