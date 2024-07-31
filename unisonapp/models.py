from django.db import models
from .views import *
# Create your models here.

class StockScreen(models.Model):
    uname = models.CharField(max_length=255),
    Stock = models.CharField(max_length=255, null=True),
    Consolidating = models.FloatField(null=True),
    Breakout = models.FloatField(null=True),
    LTP = models.FloatField(null=True),
    Volume = models.FloatField(null=True),
    MAsignal = models.CharField(max_length=255, null=True),
    RSI = models.IntegerField(null=True),
    Trend = models.CharField(max_length=255, null=True),
    Pattern = models.CharField(max_length=255, null=True)
    
