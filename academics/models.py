from django.db import models
from django.contrib.auth.models import User
from students.models import Student

class CBCPathway(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., STEM, Social Sciences, Arts & Sports")
    code = models.CharField(max_length=20, unique=True, help_text="e.g., STEM, SS, ARTS")

    def __str__(self):
        return self.name

class AcademicYear(models.Model):
    year = models.CharField(max_length=9, unique=True) # e.g., "2025/2026"
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.year

class Term(models.Model):
    name = models.CharField(max_length=20) # Term 1, Term 2, Term 3
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.academic_year}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    is_cbc = models.BooleanField(default=False, help_text="Check if this is a CBC learning area")
    is_core = models.BooleanField(default=True, help_text="Is this subject compulsory for all students?")
    pathway = models.ForeignKey(CBCPathway, on_delete=models.SET_NULL, null=True, blank=True, help_text="Leave blank if it is a Core subject")
    def __str__(self):
        return self.name

class TeacherAllocation(models.Model):
    """Assigns a teacher to a specific subject and class"""
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    # Assuming you have a ClassGroup model in students app. If not, use CharField for now.
    class_name = models.CharField(max_length=50) 
    
    def __str__(self):
        return f"{self.teacher.username} - {self.subject.name} ({self.class_name})"

# ==========================================
# 8-4-4 / KCSE GRADING SYSTEM
# ==========================================
class KCSEMarksRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    
    # 🌟 NEW: Link the mark to a specific year!
    academic_year = models.ForeignKey('AcademicYear', on_delete=models.CASCADE, null=True)
    
    cat_1 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    cat_2 = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    exam = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    grade = models.CharField(max_length=2, blank=True)
    points = models.IntegerField(default=0)

    class Meta:
        # 🌟 NEW: A student can only have ONE record per Subject, per Term, per Year.
        unique_together = ['student', 'subject', 'term', 'academic_year']

    def save(self, *args, **kwargs):
        c1 = float(self.cat_1 or 0)
        c2 = float(self.cat_2 or 0)
        ex = float(self.exam or 0)
        average_cat = (c1 + c2) / 2
        self.total_marks = int(average_cat + ex + 0.5)
        super().save(*args, **kwargs)

# ==========================================
# CBC ASSESSMENT SYSTEM
# ==========================================
class CBCStrand(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

class CBCSubStrand(models.Model):
    strand = models.ForeignKey(CBCStrand, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

class CBCAssessmentRecord(models.Model):
    RATING_CHOICES = [
        ('EE', 'Exceeding Expectation'),
        ('ME', 'Meeting Expectation'),
        ('AE', 'Approaching Expectation'),
        ('BE', 'Below Expectation'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    sub_strand = models.ForeignKey(CBCSubStrand, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    rating = models.CharField(max_length=2, choices=RATING_CHOICES)
    teacher_remarks = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['student', 'sub_strand', 'term']

class SystemLicense(models.Model):
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"License Valid Until: {self.expiry_date}"