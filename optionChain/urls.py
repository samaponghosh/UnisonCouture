from django.contrib import admin
from django.urls import path, include
from optionChain.views import *
urlpatterns = [
    path('', optionChainAna, name='home'),
    path('result', optionChainAnaResult, name='result'),
    path('refresh', resetCookies, name="refresh"),
    path('delete_old_records',  optionChainAnaResultDel, name="delete_old_records"),
    path('enter_expiry_date',  optionChainAnaExpDate, name="enter_expiry_date"),
    path('download_exel',  optionChainDownloadExel, name="download_exel")
]