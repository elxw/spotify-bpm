from django.db import models

# Create your models here.

class Playlist(models.Model):
  name = models.CharField(max_length=50, primary_key=True)
  imageUrl = models.CharField(max_length=100)
  playlistId = models.CharField(max_length=100)

class Track(models.Model):
  id = models.CharField(max_length=50, primary_key=True)
  name = models.CharField(max_length=50)
  artist = models.CharField(max_length=50)
  tempo = models.IntegerField()