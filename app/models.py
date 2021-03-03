from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class SportsURL(models.Model):

   sports = models.CharField(max_length = 30, primary_key = True)
   url = models.CharField(max_length = 200)
   sheet = models.CharField(max_length = 20)
   victory = models.IntegerField()
   rule = models.CharField(max_length = 100)
   class Meta:
      db_table = "sportsurl"