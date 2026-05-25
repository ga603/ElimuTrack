from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum

# Local app imports
from .models import StudyMaterial

# Other app imports
from academics.models import Subject, KCSEMarksRecord
from students.models import Student
from finance.models import FeeStructure, Payment

# --- TEACHER: E-Learning Dashboard ---
def elearning_dashboard(request):
    # Fetch all uploaded materials, putting the newest ones at the top
    materials = StudyMaterial.objects.all().order_by('-upload_date')
    return render(request, 'resources/dashboard.html', {'materials': materials})


# --- TEACHER: Upload Material ---
def upload_material(request, class_name):
    # TRIPWIRE 1
    print(f"========== UPLOAD PAGE OPENED FOR: {class_name} ==========")
    
    if request.method == 'POST':
        # TRIPWIRE 2
        print("========== PUBLISH BUTTON CLICKED! ==========")
        
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        video_link = request.POST.get('video_link')
        file = request.FILES.get('file')
        
        # TRIPWIRE 3
        print(f"DATA CAUGHT -> Title: {title} | Subject: {subject} | File: {file}")
        
        try:
            StudyMaterial.objects.create(
                title=title,
                subject=subject,
                target_class=class_name,
                description=description,
                video_link=video_link,
                file=file
            )
            # TRIPWIRE 4
            print("========== DATABASE SAVE SUCCESSFUL! ==========")
            messages.success(request, f"✅ Successfully published '{title}'!")
            return redirect('upload_material', class_name=class_name)
            
        except Exception as e:
            print(f"========== DATABASE CRASH: {e} ==========")
            messages.error(request, f"Error saving material: {e}")

    return render(request, 'resources/upload_material.html', {'class_name': class_name})


# --- TEACHER: Delete Material ---
def delete_material(request, material_id):
    # Find the exact material in the database
    material = get_object_or_404(StudyMaterial, id=material_id)
    
    # Save the title so we can show a success message after it's gone
    title = material.title 
    
    # Delete it!
    material.delete()
    
    messages.success(request, f"Successfully deleted '{title}'.")
    return redirect('elearning_dashboard')


# --- STUDENT: Public Access Portal ---
def student_portal(request):
    adm_no = request.GET.get('adm_no')
    context = {}

    if adm_no:
        try:
            # 1. Fetch Student
            student = Student.objects.get(admission_number=adm_no)
            context['student'] = student
            
            # 2. Fetch Academic History
            marks_history = KCSEMarksRecord.objects.filter(student=student).order_by('-academic_year', '-term')
            context['marks_history'] = marks_history

            # 3. Fetch E-Learning Materials matching this student's exact class
            materials = StudyMaterial.objects.filter(target_class=student.current_class).order_by('-upload_date')
            context['materials'] = materials
            
        except Student.DoesNotExist:
            context['error'] = f"No student found with Admission No '{adm_no}'."

    return render(request, 'resources/student_portal.html', context)