from django.contrib import admin
from django.urls import path, include
from optionChain.views import *
urlpatterns = [
    path('', optionChainAna, name='home'),
    path('stock', optionChainAnaStock, name='stock'),
    path('result', optionChainAnaResult, name='result'),
    path('resultAJAX', optionChainAnaResultAjax, name='resultAJAX'),
    path('refresh', resetCookies, name="refresh"),
    path('delete_old_records',  optionChainAnaResultDel, name="delete_old_records"),
    path('enter_expiry_date',  optionChainAnaExpDate, name="enter_expiry_date"),
    path('stock/enter_expiry_date',  optionChainAnaExpDateStock, name="stock/enter_expiry_date"),
    path('download_exel',  optionChainDownloadExel, name="download_exel")
]