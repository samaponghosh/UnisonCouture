from django.db import models

# Create your models here.
class NSEOptionChainAnalyzer(models.Model):
    uname = models.CharField(max_length=255, null=True)
    index = models.CharField(max_length=255, null=True)
    stock = models.CharField(max_length=255, null=True)
    option_mode = models.CharField(max_length=100, null=True)
    expiry_date = models.CharField(max_length=255, null=True)
    sp_entry = models.FloatField(null=True)
    str_current_time = models.CharField(max_length=255, null=True)
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
    old_points = models.FloatField(null=True)
    old_points_color = models.CharField(max_length=10, null = True)
    old_call_sum = models.FloatField(null=True)
    old_call_sum_color = models.CharField(max_length=10, null = True)
    old_put_sum = models.FloatField(null=True) 
    old_put_sum_color = models.CharField(max_length=10, null = True)
    old_difference = models.FloatField(null=True) 
    old_difference_color = models.CharField(max_length=10, null = True)
    old_call_boundary = models.FloatField(null=True) 
    old_call_boundary_color =models.CharField(max_length=10, null = True)
    old_put_boundary = models.FloatField(null=True) 
    old_put_boundary_color = models.CharField(max_length=10, null = True)
    old_call_itm = models.FloatField(null=True) 
    old_call_itm_color = models.CharField(max_length=10, null = True)
    old_put_itm = models.FloatField(null=True)
    old_put_itm_color = models.CharField(max_length=10, null = True)
    
    def get_id(self):
        return self.id
    
class IndexExpDates(models.Model):
    index = models.CharField(max_length=255)
    expiry_date = models.CharField(max_length=255)
    
    def get_id(self):
        return self.id

class StockOptions(models.Model):
    Indices = models.CharField(max_length=255)

class UserInputs(models.Model):
    uname = models.CharField(max_length=255)
    option_mode = models.CharField(max_length=100)
    index = models.CharField(max_length=255)
    sp_entry = models.FloatField()
    expiry_date = models.CharField(max_length=255, null=True)
    query_datetime = models.DateTimeField()
    
    def get_id(self):
        return self.id

    
    