from django.db import models

# Create your models here.
class NSEOptionChainAnalyzer(models.Model):
    uname = models.CharField(max_length=255)
    index = models.CharField(max_length=255)
    stock = models.CharField(max_length=255)
    expiry_date = models.CharField(max_length=255)
    sp_entry = models.FloatField()
    str_current_time = models.CharField(max_length=255)
    points = models.FloatField()
    call_sum = models.FloatField()
    put_sum = models.FloatField()
    difference = models.FloatField()
    call_boundary = models.FloatField()
    put_boundary = models.FloatField()
    call_itm = models.FloatField()
    put_itm = models.FloatField()
    oi_label = models.CharField(max_length=50)
    put_call_ratio = models.FloatField()  
    call_exits_label = models.CharField(max_length=10) 
    call_itm_val = models.CharField(max_length=10) 
    put_exits_label = models.CharField(max_length=10)
    put_itm_val = models.CharField(max_length=10)

class IndexExpDates(models.Model):
    index = models.CharField(max_length=255)
    expiry_date = models.CharField(max_length=255)

    
    