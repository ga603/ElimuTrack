from django.urls import path
from . import views

urlpatterns = [
    # The new spreadsheet page
    # Add <str:class_name>/ to the URL
    path('enter-marks/<str:class_name>/', views.enter_marks, name='enter_marks'),
    
    # The invisible AJAX background saver
    path('ajax/save-marks/', views.save_marks_ajax, name='save_marks_ajax'), 
    path('report-card/<int:student_id>/', views.student_report_card, name='student_report_card'),
    path('system-locked/', views.unlock_system, name='unlock_system'),
    path('report-card/<int:student_id>/', views.student_report_card, name='student_report_card'),
    path('bulk-reports/<str:class_name>/', views.bulk_report_cards, name='bulk_report_cards'),
]