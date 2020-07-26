from musicwire.core.helpers import generate_uniq_id
from django.db import models


class UserProfile(models.Model):
    username = models.CharField(max_length=155)
    password = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    token = models.CharField(max_length=50, default=generate_uniq_id)