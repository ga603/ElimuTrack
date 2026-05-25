from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.class_dashboard, name='class_dashboard'),
    path('', views.student_list, name='student_list'),
    path('add/', views.add_student, name='add_student'),
    # This <int:pk> allows us to view specific students by their ID
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('class/<str:class_name>/', views.single_class_view, name='single_class_view'),
    path('class/<str:class_name>/promote/', views.promote_class, name='promote_class'),
    path('edit/<int:pk>/', views.edit_student, name='edit_student'),
    path('delete/<int:pk>/', views.delete_student, name='delete_student'),
    path('bulk-upload/', views.bulk_upload_students, name='bulk_upload_students'),
]