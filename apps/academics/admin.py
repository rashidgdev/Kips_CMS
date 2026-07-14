from django.contrib import admin

from .models import Course, CourseOffering, Enrollment, Program, Semester


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'degree_level', 'total_semesters', 'is_active')
    list_filter = ('degree_level', 'is_active', 'department')
    search_fields = ('code', 'name')
    autocomplete_fields = ('department',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('program', 'number', 'academic_year', 'is_current', 'start_date', 'end_date')
    list_filter = ('program', 'is_current', 'academic_year')
    search_fields = ('program__code', 'program__name', 'name')
    autocomplete_fields = ('program',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'program', 'semester_number', 'credit_hours', 'course_type', 'is_active')
    list_filter = ('program', 'course_type', 'is_active')
    search_fields = ('code', 'title')
    autocomplete_fields = ('program',)


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('course', 'semester', 'teacher', 'section', 'max_seats', 'is_active')
    list_filter = ('semester', 'is_active')
    search_fields = ('course__code', 'course__title', 'teacher__employee_id')
    autocomplete_fields = ('course', 'semester', 'teacher', 'assigned_by')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_offering', 'status', 'enrolled_at')
    list_filter = ('status',)
    search_fields = ('student__roll_number', 'course_offering__course__code')
    autocomplete_fields = ('student', 'course_offering')
