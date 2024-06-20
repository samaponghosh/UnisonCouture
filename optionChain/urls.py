from django.contrib import admin
from django.urls import path, include
from optionChain.views import *
urlpatterns = [
    path('', optionChainAna, name='home'),
    path('result', optionChainAnaResult, name='result'),
    path('refresh', resetCookies, name="refresh"),
]