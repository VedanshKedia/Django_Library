from django.db import models
# from django.contrib.auth.models import User
# from django.contrib.postgres.fields import ArrayField
# from embed_video.fields import EmbedVideoField
# Create your models here.


class Item(models.Model):
    video = models.TextField()  # same like models.URLField()

    def __str__(self):
        return f'{self.video}'
