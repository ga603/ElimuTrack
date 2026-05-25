from django.db import models

class Student(models.Model):
    SYSTEM_CHOICES = [
        ('CBC', 'CBC (Grade 10-12)'),
        ('844', '8-4-4 (Form 3-4)'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'), 
    ]

    # --- NEW: Strict Class Options ---
    CLASS_CHOICES = [
        ('Grade 10', 'Grade 10'),
        ('Grade 11', 'Grade 11'),
        ('Grade 12', 'Grade 12'),
        ('Form 3', 'Form 3'),
        ('Form 4', 'Form 4'),
    ]
    PATHWAY_CHOICES = [
        ('STEM', 'STEM (Science, Tech, Engineering, Math)'),
        ('ARTS', 'Arts and Sports Science'),
        ('SOCIAL', 'Social Sciences'),
    ]

    # --- Student Details ---
    admission_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    
    passport_photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)

    # --- Academic Info ---
    curriculum = models.CharField(max_length=5, choices=SYSTEM_CHOICES, default='CBC')
    
    # UPDATED: Now uses a dropdown instead of text input
    current_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    
    cbc_pathway = models.ForeignKey('academics.CBCPathway', on_delete=models.SET_NULL, null=True, blank=True, help_text="Only needed for Grade 10-12 students")
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(blank=True, null=True)

    # --- System Data ---
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    admission_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_number})"