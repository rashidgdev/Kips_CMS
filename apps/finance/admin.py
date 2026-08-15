from django.contrib import admin

from .models import Challan, ChallanLine, FeeCategory, FeeStructure, Payment, StudentFeeItem, StudentFeeOverride


@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('program', 'category', 'amount', 'is_recurring')
    list_filter = ('program', 'is_recurring')
    autocomplete_fields = ('program', 'category')


@admin.register(StudentFeeOverride)
class StudentFeeOverrideAdmin(admin.ModelAdmin):
    list_display = ('student', 'category', 'amount', 'is_recurring')
    list_filter = ('category', 'is_recurring')
    search_fields = ('student__roll_number', 'student__user__first_name', 'student__user__last_name')
    autocomplete_fields = ('student', 'category')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    autocomplete_fields = ('received_by',)


@admin.register(StudentFeeItem)
class StudentFeeItemAdmin(admin.ModelAdmin):
    list_display = ('student', 'category', 'semester', 'amount_due', 'due_date')
    list_filter = ('category', 'semester')
    search_fields = ('student__roll_number', 'student__user__first_name', 'student__user__last_name')
    autocomplete_fields = ('student', 'category', 'semester')
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('fee_item', 'amount_paid', 'payment_date', 'payment_method', 'received_by')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('fee_item__student__roll_number',)
    autocomplete_fields = ('fee_item', 'received_by')


class ChallanLineInline(admin.TabularInline):
    model = ChallanLine
    extra = 0
    autocomplete_fields = ('fee_item',)


@admin.register(Challan)
class ChallanAdmin(admin.ModelAdmin):
    list_display = ('challan_number', 'student', 'semester', 'issue_date', 'due_date', 'total_amount', 'is_cancelled')
    list_filter = ('semester', 'is_cancelled')
    search_fields = ('challan_number', 'student__roll_number')
    autocomplete_fields = ('student', 'semester', 'created_by')
    inlines = [ChallanLineInline]
