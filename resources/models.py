from django.db import models
from academics.models import Subject
from django.utils import timezone

class StudyMaterial(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    target_class = models.CharField(max_length=50) # e.g., Grade 10, Form 3
    description = models.TextField(blank=True, null=True)
    
    # The File Upload (PDFs, Word docs) - Optional
    file = models.FileField(upload_to='study_materials/', blank=True, null=True)
    
    # 🌟 NEW: The Video Link (YouTube, Zoom) - Optional
    video_link = models.URLField(max_length=500, blank=True, null=True)
    
    upload_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.target_class})"

# FIXED: Notice is now properly un-indented so it is its own standalone table
class Notice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True, help_text="Visible to all staff and parents")

    def __str__(self):
        return self.title