from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class SportsURL(models.Model):

   sports = models.CharField(max_length = 20, primary_key = True)
   url = models.CharField(max_length = 200)
   class Meta:
      db_table = "sportsurl"