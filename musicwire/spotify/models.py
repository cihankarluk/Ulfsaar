from django.db import models


class Spotify(models.Model):
    base_url = models.CharField(max_length=255)
