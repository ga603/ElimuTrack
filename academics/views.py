import json
import hashlib
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Cleaned up imports (no duplicates)
from .models import KCSEMarksRecord, Subject, Term, AcademicYear, SystemLicense, CBCPathway
from students.models import Student

# --- THE 8-4-4 KCSE GRADING ENGINE ---
def get_kcse_grade(total_marks):
    try:
        total = float(total_marks)
    except (ValueError, TypeError):
        return '-', 0
        
    if total >= 80: return 'A', 12
    elif total >= 75: return 'A-', 11
    elif total >= 70: return 'B+', 10
    elif total >= 65: return 'B', 9
    elif total >= 60: return 'B-', 8
    elif total >= 55: return 'C+', 7
    elif total >= 50: return 'C', 6
    elif total >= 45: return 'C-', 5
    elif total >= 40: return 'D+', 4
    elif total >= 35: return 'D', 3
    elif total >= 30: return 'D-', 2
    else: return 'E', 1

# --- THE CBC SENIOR SCHOOL GRADING ENGINE ---
def get_cbc_grade(total_marks):
    try:
        total = float(total_marks)
    except (ValueError, TypeError):
        return '-', 0
        
    if total >= 80: return 'EE', 4     # Exceeding Expectations
    elif total >= 65: return 'ME', 3   # Meeting Expectations
    elif total >= 50: return 'AE', 2   # Approaching Expectations
    else: return 'BE', 1               # Below Expectations

# --- THE SPREADSHEET PAGE ---
def enter_marks(request, class_name):
    subject_id = request.GET.get('subject_id')
    term_id = request.GET.get('term_id')
    pathway_id = request.GET.get('pathway_id')
    year_id = request.GET.get('year_id') # 🌟 CATCH THE YEAR

    is_cbc = 'grade' in class_name.lower()

    # SCENARIO A: Show the Gateway form!
    if not subject_id or not term_id or not year_id:
        subjects = Subject.objects.all()
        terms = Term.objects.all()
        years = AcademicYear.objects.all() # 🌟 FETCH THE YEARS
        pathways = CBCPathway.objects.all() if is_cbc else None

        return render(request, 'academics/select_assessment.html', {
            'current_class': class_name,
            'subjects': subjects,
            'terms': terms,
            'years': years,       # 🌟 SEND TO HTML
            'pathways': pathways, 
            'is_cbc': is_cbc      
        })

    # SCENARIO B: Subject picked! Show the Marks Grid!
    subject = get_object_or_404(Subject, id=subject_id)
    term = get_object_or_404(Term, id=term_id)       
    academic_year = get_object_or_404(AcademicYear, id=year_id) # 🌟 GET THE YEAR OBJECT
    
    # FILTER THE STUDENTS!
    if is_cbc and pathway_id:
        students = Student.objects.filter(current_class=class_name, cbc_pathway_id=pathway_id).order_by('admission_number')
    else:
        students = Student.objects.filter(current_class=class_name).order_by('admission_number')

    records = []
    for student in students:
        # 🌟 NEW: The grid now looks for the specific Term AND Year!
        record, created = KCSEMarksRecord.objects.get_or_create(
            student=student, subject=subject, term=term, academic_year=academic_year
        )
        records.append(record)
            
    return render(request, 'academics/enter_marks.html', {
        'records': records,
        'subject': subject,
        'term': term,
        'current_class': class_name
    })

# --- THE AJAX HYBRID AUTO-SAVE API ---
@csrf_exempt
def save_marks_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            record_id = data.get('record_id')
            
            # Convert inputs to floats (defaulting to 0 if left blank)
            cat_1 = float(data.get('cat_1') or 0.0)
            cat_2 = float(data.get('cat_2') or 0.0)
            exam = float(data.get('exam') or 0.0)

            record = get_object_or_404(KCSEMarksRecord, id=record_id)
            
            # Update the individual fields
            record.cat_1 = cat_1
            record.cat_2 = cat_2
            record.exam = exam

           # THE MATH: Average the CATs (out of 30) + Exam (out of 70)
            average_cat = (cat_1 + cat_2) / 2
            
            # The + 0.5 forces strict academic rounding (e.g. 59.5 becomes 60.0), 
            # and int() chops off the decimals to make it a clean whole number!
            total_marks = int(average_cat + exam + 0.5) 
            
            record.total_marks = total_marks

            # --- DUAL-CURRICULUM GRADING LOGIC ---
            # Automatically check if the student is in a "Grade" (CBC) or "Form" (8-4-4)
            is_cbc = 'grade' in record.student.current_class.lower()
            
            if is_cbc:
                grade, points = get_cbc_grade(total_marks)
            else:
                grade, points = get_kcse_grade(total_marks)
            
            record.grade = grade
            record.save()

            # Send the total and grade back to the screen instantly
            return JsonResponse({
                'status': 'success',
                'total': record.total_marks,
                'grade': record.grade
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'invalid_method'}, status=405)


# --- REPORT CARD LOGIC ---
def student_report_card(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    records = KCSEMarksRecord.objects.filter(student=student)
    
    total_score = sum(record.total_marks for record in records if record.total_marks)
    subjects_count = records.count()
    average = (total_score / subjects_count) if subjects_count > 0 else 0
    
    is_cbc = 'grade' in student.current_class.lower()
    
    if is_cbc:
        overall_grade, _ = get_cbc_grade(average)
    else:
        overall_grade, _ = get_kcse_grade(average)

    return render(request, 'academics/report_card.html', {
        'student': student,
        'records': records,
        'total_score': total_score,
        'average': round(average, 2),
        'overall_grade': overall_grade,
        'is_cbc': is_cbc
    })


# --- LICENSE LOGIC ---
def unlock_system(request):
    error_message = None
    if request.method == 'POST':
        entered_key = request.POST.get('license_key', '').strip()

        try:
            parts = entered_key.split('-')
            if len(parts) == 3 and parts[0] == 'ELIMU':
                days = int(parts[1])
                expected_hash = hashlib.md5(f"MachakosCEO2026{days}".encode()).hexdigest()[:6].upper()
                
                if parts[2].upper() == expected_hash:
                    license_obj, created = SystemLicense.objects.get_or_create(id=1, defaults={'expiry_date': date.today()})
                    license_obj.expiry_date = date.today() + timedelta(days=days)
                    license_obj.is_active = True
                    license_obj.save()
                    return redirect('enter_marks')
                else:
                    error_message = "Invalid license key format or hash."
            else:
                error_message = "License key must be in the format: ELIMU-{Days}-{Hash}"
        except Exception as e:
            error_message = f"Error processing license key: {str(e)}"
            
    license_obj = SystemLicense.objects.first()
    return render(request, 'academics/unlock.html', {'license': license_obj, 'error': error_message})

def bulk_report_cards(request, class_name):
    # 1. Get all students in this specific class
    students = Student.objects.filter(current_class=class_name).order_by('admission_number')
    is_cbc = 'grade' in class_name.lower()
    
    class_reports = []
    
    # 2. Loop through every student and calculate their stats
    for student in students:
        records = KCSEMarksRecord.objects.filter(student=student)
        
        # Only generate a report if the student actually has marks entered!
        if records.exists():
            total_score = sum(record.total_marks for record in records if record.total_marks)
            subjects_count = records.count()
            average = (total_score / subjects_count) if subjects_count > 0 else 0
            
            if is_cbc:
                overall_grade, _ = get_cbc_grade(average)
            else:
                overall_grade, _ = get_kcse_grade(average)
                
            # 3. Bundle this student's data and add it to the master list
            class_reports.append({
                'student': student,
                'records': records,
                'total_score': total_score,
                'average': round(average, 2),
                'overall_grade': overall_grade,
            })

    return render(request, 'academics/bulk_report_cards.html', {
        'class_reports': class_reports,
        'class_name': class_name,
        'is_cbc': is_cbc
    })