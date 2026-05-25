from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'first_name', 'current_class', 'curriculum', 'parent_phone', 'status')
    search_fields = ('admission_number', 'first_name', 'last_name')
    list_filter = ('curriculum', 'current_class', 'status')

