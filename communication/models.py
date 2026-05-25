from django.db import models
from students.models import Student

class SMSLog(models.Model):
    PURPOSE_CHOICES = [
        ('GENERAL', 'General Announcement'),
        ('FEES', 'Fee Reminder'),
        ('ACADEMIC', 'Academic Report'),
        ('EMERGENCY', 'Emergency Alert'),
    ]

    recipient = models.ForeignKey(Student, on_delete=models.CASCADE, help_text="Student whose parent received the SMS")
    phone_number = models.CharField(max_length=15)
    message_body = models.TextField()
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='GENERAL')
    status = models.CharField(max_length=10, default='Sent') # In real API, this would update based on delivery
    date_sent = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"To {self.recipient} - {self.date_sent.strftime('%Y-%m-%d')}"