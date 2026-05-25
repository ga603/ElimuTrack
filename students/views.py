from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from .models import Student
from .forms import StudentForm
import csv

# --- 1. CLASS MANAGEMENT DASHBOARD ---
@login_required
def class_dashboard(request):
    """Shows fixed cards for Grade 10-12 and Form 3-4."""
    standard_classes = ['Grade 10', 'Grade 11', 'Grade 12', 'Form 3', 'Form 4']
    class_data = []
    
    for cls in standard_classes:
        # Count active students in this class
        count = Student.objects.filter(current_class=cls, status='ACTIVE').count()
        class_data.append({'current_class': cls, 'count': count})
        
    return render(request, 'students/class_dashboard.html', {'classes': class_data})

@login_required
def single_class_view(request, class_name):
    """The Command Center for a specific class (Attendance, Marks, etc.)"""
    students = Student.objects.filter(current_class=class_name)
    return render(request, 'students/single_class_view.html', {
        'class_name': class_name, 
        'students': students
    })

@login_required
def promote_class(request, class_name):
    """Logic to automatically move students to the next grade."""
    if request.method == 'POST':
        students = Student.objects.filter(current_class=class_name)
        
        # Define the path: 'Current Class' -> 'Next Class'
        progression = {
            'Grade 10': 'Grade 11',
            'Grade 11': 'Grade 12',
            'Grade 12': 'Alumni',
            'Form 3': 'Form 4',
            'Form 4': 'Alumni',
        }
        
        next_class = progression.get(class_name)
        
        if next_class:
            count = students.update(current_class=next_class)
            messages.success(request, f"Successfully promoted {count} students from {class_name} to {next_class}!")
        else:
            messages.error(request, f"No promotion path defined for {class_name}. Please update manually.")
            
        return redirect('class_dashboard')
    
    return render(request, 'students/confirm_promote.html', {'class_name': class_name})


# --- 2. EXISTING STUDENT MANAGEMENT (Search, Add, Detail) ---

@login_required
def student_list(request):
    """General list of all students with Search functionality."""
    query = request.GET.get('q') # Get the search text
    if query:
        # Search by name or admission number
        students = Student.objects.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(admission_number__icontains=query)
        )
    else:
        students = Student.objects.all()
        
    return render(request, 'students/student_list.html', {'students': students, 'query': query})

@login_required
def student_detail(request, pk):
    """View full profile of a single student."""
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'students/student_detail.html', {'student': student})

@login_required
def add_student(request):
    """Form to register a new student."""
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added successfully!')
            return redirect('class_dashboard') # Redirect to the new dashboard
    else:
        form = StudentForm()
    return render(request, 'students/add_student.html', {'form': form})
login_required
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student details updated successfully!')
            return redirect('student_detail', pk=student.pk)
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/add_student.html', {'form': form, 'title': 'Edit Student'})
@login_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        class_name = student.current_class
        student.delete()
        messages.warning(request, 'Student deleted permanently.')
        return redirect('single_class_view', class_name=class_name)
        
    return render(request, 'students/confirm_delete.html', {'student': student})

def bulk_upload_students(request):
    if request.method == 'POST' and request.FILES.get('student_file'):
        csv_file = request.FILES['student_file']
        
        # Security check
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Error: Please upload a .CSV file.')
            return redirect('bulk_upload_students')
            
        try:
            # Read and decode the file
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            # Loop through Excel rows and save to database
            count = 0
            for row in reader:
                # FIX: Split the single Excel name into First and Last names
                raw_name = row.get('Name', '').strip()
                name_parts = raw_name.split(' ', 1) # Splits at the first space
                f_name = name_parts[0] if len(name_parts) > 0 else 'Unknown'
                l_name = name_parts[1] if len(name_parts) > 1 else ''

                # Get or Create prevents duplicate admission numbers from crashing the system
                student, created = Student.objects.get_or_create(
                    admission_number=row.get('Adm No'),
                    defaults={
                        'first_name': f_name,
                        'last_name': l_name,
                        'current_class': row.get('Class'),
                        'parent_phone': row.get('Parent Phone', '0000000000'),
                        'date_of_birth': '2010-01-01'  # <-- THE FIX: A default placeholder birthday!
                    }
                )
                if created:
                    count += 1
                    
            messages.success(request, f'Success! {count} new students were uploaded to the system.')
        except Exception as e:
            messages.error(request, f'Error reading file. Ensure headers match exactly: Adm No, Name, Class, Parent Phone. Details: {e}')
            
        return redirect('bulk_upload_students') 

    return render(request, 'students/upload_students.html')