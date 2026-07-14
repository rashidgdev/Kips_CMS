from django.contrib import admin

from .models import DayBookEntry, MonthlyWorkloadSnapshot


@admin.register(DayBookEntry)
class DayBookEntryAdmin(admin.ModelAdmin):
    list_display = ('session', 'is_verified', 'verified_by', 'verified_at')
    list_filter = ('verified_by',)
    search_fields = ('session__course_offering__course__code',)
    autocomplete_fields = ('session', 'verified_by')


@admin.register(MonthlyWorkloadSnapshot)
class MonthlyWorkloadSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        'teacher', 'year', 'month', 'total_lectures', 'verified_lectures', 'per_lecture_rate',
        'total_amount', 'generated_by',
    )
    list_filter = ('year', 'month')
    search_fields = ('teacher__employee_id', 'teacher__user__first_name', 'teacher__user__last_name')
    autocomplete_fields = ('teacher', 'generated_by')
