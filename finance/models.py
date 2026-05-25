from django.db import models
from students.models import Student

class FeeStructure(models.Model):
    TERM_CHOICES = [('Term 1', 'Term 1'), ('Term 2', 'Term 2'), ('Term 3', 'Term 3')]
    
    class_name = models.CharField(max_length=50, help_text="e.g. Grade 10")
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    year = models.IntegerField(default=2025)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Required Fee Amount (KES)")

    class Meta:
        unique_together = ['class_name', 'term', 'year']

    def __str__(self):
        return f"{self.class_name} - {self.term} ({self.amount})"

class Payment(models.Model):
    METHOD_CHOICES = [
        ('MPESA', 'M-Pesa'),
        ('BANK', 'Bank Deposit'),
        ('CASH', 'Cash'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    transaction_reference = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. M-Pesa Code")
    term = models.CharField(max_length=20, choices=FeeStructure.TERM_CHOICES, default='Term 1')
    
    def __str__(self):
        return f"{self.student} - {self.amount_paid}"