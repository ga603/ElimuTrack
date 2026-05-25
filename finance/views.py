from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import FeeStructure, Payment
from students.models import Student
from django.contrib import messages

@login_required
def finance_dashboard(request):
    # This view shows a list of students with their fee balances
    students = Student.objects.all()
    student_data = []

    for student in students:
        # 1. Get Fee Structure for this student's class
        structure = FeeStructure.objects.filter(class_name=student.current_class, term='Term 1', year=2025).first()
        required_amount = structure.amount if structure else 0

        # 2. Calculate Total Paid
        total_paid = Payment.objects.filter(student=student, term='Term 1').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0

        # 3. Calculate Balance
        balance = required_amount - total_paid

        student_data.append({
            'student': student,
            'required': required_amount,
            'paid': total_paid,
            'balance': balance,
            'status': 'Cleared' if balance <= 0 else 'Defaulter'
        })

    return render(request, 'finance/dashboard.html', {'data': student_data})

@login_required
def record_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        method = request.POST.get('method')
        ref = request.POST.get('ref')
        
        Payment.objects.create(
            student=student,
            amount_paid=amount,
            payment_method=method,
            transaction_reference=ref,
            term='Term 1' # Defaulting to Term 1 for now
        )
        messages.success(request, f"Payment of KES {amount} recorded for {student.first_name}")
        return redirect('finance_dashboard')

    return render(request, 'finance/record_payment.html', {'student': student})

def initiate_public_payment(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')
        
        # --- HERE WE WOULD TRIGGER THE M-PESA STK PUSH ---
        # mpesa_api.stk_push(phone, amount)
        
        # For now, we simulate a successful request
        messages.success(request, f"Payment request sent to {phone}. Please enter your M-Pesa PIN.")
        return redirect('student_portal') # Send them back to portal

    return render(request, 'finance/public_pay.html', {'student': student})