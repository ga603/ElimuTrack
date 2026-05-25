from django.urls import path
from . import views

urlpatterns = [
    path('', views.finance_dashboard, name='finance_dashboard'),
    path('pay/<int:student_id>/', views.record_payment, name='record_payment'),
    path('public-pay/<int:student_id>/', views.initiate_public_payment, name='initiate_public_payment'),
]