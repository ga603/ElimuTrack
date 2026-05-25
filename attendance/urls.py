from django.urls import path
from . import views

urlpatterns = [
    # The main attendance screen (replaces 'attendance_dashboard')
    path('select/', views.select_class, name='select_class'),
    
    # The actual register for a specific class
    path('mark/<str:class_name>/', views.mark_attendance, name='mark_attendance'),
    
    # The Excel download
    path('export/<str:class_name>/', views.export_attendance, name='export_attendance'),
]