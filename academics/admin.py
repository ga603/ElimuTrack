from django.contrib import admin

from .models import (
    CBCPathway, AcademicYear, Term, Subject, TeacherAllocation, 
    KCSEMarksRecord, CBCStrand, CBCSubStrand, CBCAssessmentRecord
)

# Registering the new core setup models
admin.site.register(CBCPathway)
admin.site.register(AcademicYear)
admin.site.register(Term)
admin.site.register(Subject)
admin.site.register(TeacherAllocation)

# Registering the new grading engines
admin.site.register(KCSEMarksRecord)
admin.site.register(CBCStrand)
admin.site.register(CBCSubStrand)
admin.site.register(CBCAssessmentRecord)