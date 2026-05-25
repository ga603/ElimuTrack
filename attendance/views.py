import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from students.models import Student
from .models import Attendance
from datetime import date

@login_required
def select_class(request):
    # Get a list of all unique classes (e.g., Grade 10, Form 3)
    classes = Student.objects.values_list('current_class', flat=True).distinct()
    return render(request, 'attendance/select_class.html', {'classes': classes})

@login_required
def mark_attendance(request, class_name):
    students = Student.objects.filter(current_class=class_name)
    today = date.today()

    if request.method == 'POST':
        # Loop through every student and get their status from the form
        for student in students:
            status = request.POST.get(f'status_{student.id}')
            remarks = request.POST.get(f'remarks_{student.id}')
            
            # Save or Update the attendance record
            Attendance.objects.update_or_create(
                student=student,
                date=today,
                defaults={'status': status, 'remarks': remarks}
            )
        messages.success(request, f'Attendance for {class_name} marked successfully!')
        return redirect('select_class')

    return render(request, 'attendance/mark_register.html', {
        'students': students, 
        'class_name': class_name,
        'today': today
    })
def export_attendance(request, class_name):
    # Fetch all records for this class, ordered by date
    records = Attendance.objects.filter(student__current_class=class_name).order_by('-date', 'student__first_name')
    
    # Create the CSV response (Downloadable file)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{class_name}_Attendance_Report.csv"'
    
    writer = csv.writer(response)
    # Write the Header Row
    writer.writerow(['Date', 'Admission No', 'Student Name', 'Status', 'Remarks'])
    
    # Write Data Rows
    for record in records:
        writer.writerow([
            record.date,
            record.student.admission_number,
            f"{record.student.first_name} {record.student.last_name}",
            record.get_status_display(), # Shows "Present" instead of "PRESENT"
            record.remarks
        ])
        
    return response