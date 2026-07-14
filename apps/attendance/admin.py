from django.contrib import admin

from .models import AttendanceRecord, LectureSession


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    autocomplete_fields = ('student', 'marked_by')


@admin.register(LectureSession)
class LectureSessionAdmin(admin.ModelAdmin):
    list_display = ('course_offering', 'date', 'start_time', 'end_time', 'created_by')
    list_filter = ('course_offering__semester', 'date')
    search_fields = ('course_offering__course__code', 'course_offering__course__title')
    autocomplete_fields = ('course_offering', 'created_by')
    inlines = [AttendanceRecordInline]


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status', 'marked_by', 'marked_at')
    list_filter = ('status',)
    search_fields = ('student__roll_number', 'session__course_offering__course__code')
    autocomplete_fields = ('session', 'student', 'marked_by')
