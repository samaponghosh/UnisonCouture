from django.db import models
# from .views import *
# Create your models here.

class StockScreen(models.Model):
    uname = models.CharField(max_length=255)
    Stock = models.CharField(max_length=255, null=True)
    Consolidating = models.CharField(max_length=255, null=True)
    Breakout = models.CharField(max_length=255, null=True)
    LTP = models.CharField(max_length=255, null=True)
    Volume = models.CharField(max_length=255, null=True)
    MAsignal = models.CharField(max_length=255, null=True)
    RSI = models.CharField(max_length=255,null=True)
    Trend = models.CharField(max_length=255, null=True)
    Pattern = models.CharField(max_length=255, null=True)
    
    class Meta:
        db_table = 'StockScreen'
    
