from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_bulk_sms, name='send_bulk_sms'),
    path('history/', views.sms_history, name='sms_history'),
]