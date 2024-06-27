from django.db import models

# Create your models here.
class NSEOptionChainAnalyzer(models.Model):
    uname = models.CharField(max_length=255)
    index = models.CharField(max_length=255)
    stock = models.CharField(max_length=255, null=True)
    expiry_date = models.CharField(max_length=255, null=True)
    sp_entry = models.FloatField()
    str_current_time = models.CharField(max_length=255)
    points = models.FloatField( null=True)
    call_sum = models.FloatField( null=True)
    put_sum = models.FloatField( null=True)
    difference = models.FloatField( null=True)
    call_boundary = models.FloatField( null=True)
    put_boundary = models.FloatField( null=True)
    call_itm = models.FloatField( null=True)
    put_itm = models.FloatField( null=True)
    oi_label = models.CharField(max_length=50,  null=True)
    put_call_ratio = models.FloatField( null=True)  
    call_exits_label = models.CharField(max_length=10, null=True) 
    call_itm_val = models.CharField(max_length=10, null=True) 
    put_exits_label = models.CharField(max_length=10, null=True)
    put_itm_val = models.CharField(max_length=10, null=True)

class IndexExpDates(models.Model):
    index = models.CharField(max_length=255)
    expiry_date = models.CharField(max_length=255)

class StockOptions(models.Model):
    Indices = models.CharField(max_length=255)

    
    