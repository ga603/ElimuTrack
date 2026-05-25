from django.urls import path
from . import views

urlpatterns = [
    path('portal/', views.student_portal, name='student_portal'),
    path('dashboard/', views.elearning_dashboard, name='elearning_dashboard'),
    path('delete/<int:material_id>/', views.delete_material, name='delete_material'),
    
    # The absolute exact route for uploads
    path('upload/<str:class_name>/', views.upload_material, name='upload_material'),
]