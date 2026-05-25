from django.contrib import admin
from .models import FeeStructure, Payment

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'term', 'amount')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount_paid', 'date_paid', 'payment_method')
    list_filter = ('payment_method', 'date_paid')