from django.db import models
from students.models import Student # <--- Link to your existing students

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    remarks = models.CharField(max_length=200, blank=True, null=True, help_text="Reason for absence")

    class Meta:
        # Prevent marking the same student twice on the same day
        unique_together = ['student', 'date']

    def __str__(self):
        return f"{self.student.first_name} - {self.date} - {self.status}"