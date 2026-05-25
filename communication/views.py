from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from students.models import Student
from .models import SMSLog

@login_required
def send_bulk_sms(request):
    # Get all classes for the dropdown
    classes = Student.objects.values_list('current_class', flat=True).distinct()
    
    if request.method == 'POST':
        target_class = request.POST.get('target_class')
        message = request.POST.get('message')
        purpose = request.POST.get('purpose')
        
        # 1. Filter the students
        if target_class == 'ALL':
            recipients = Student.objects.all()
        else:
            recipients = Student.objects.filter(current_class=target_class)
            
        count = 0
        for student in recipients:
            if student.parent_phone:
                # --- REAL SMS API CODE WOULD GO HERE ---
                # Example: africastalking.send(student.parent_phone, message)
                
                # 2. Log the message in our database
                SMSLog.objects.create(
                    recipient=student,
                    phone_number=student.parent_phone,
                    message_body=message,
                    purpose=purpose
                )
                count += 1
                
        messages.success(request, f"Successfully queued {count} messages to {target_class} parents.")
        return redirect('sms_history')

    return render(request, 'communication/send_sms.html', {'classes': classes})

@login_required
def sms_history(request):
    logs = SMSLog.objects.all().order_by('-date_sent')
    return render(request, 'communication/sms_history.html', {'logs': logs})