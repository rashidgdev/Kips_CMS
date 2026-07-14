from django.contrib import admin

from .models import Assessment, AssessmentCategory, CourseResult, Mark, SemesterGPA


@admin.register(AssessmentCategory)
class AssessmentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_weight_percent')
    search_fields = ('name',)


class MarkInline(admin.TabularInline):
    model = Mark
    extra = 0
    autocomplete_fields = ('student', 'graded_by')


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('course_offering', 'category', 'title', 'total_marks', 'weight_percent', 'date')
    list_filter = ('category', 'course_offering__semester')
    search_fields = ('title', 'course_offering__course__code')
    autocomplete_fields = ('course_offering', 'category', 'created_by')
    inlines = [MarkInline]


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ('student', 'assessment', 'obtained_marks', 'graded_by', 'graded_at')
    search_fields = ('student__roll_number', 'assessment__title')
    autocomplete_fields = ('assessment', 'student', 'graded_by')


@admin.register(CourseResult)
class CourseResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'course_offering', 'total_obtained', 'total_possible', 'percentage', 'grade_letter')
    list_filter = ('grade_letter',)
    search_fields = ('student__roll_number', 'course_offering__course__code')
    autocomplete_fields = ('student', 'course_offering')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SemesterGPA)
class SemesterGPAAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'gpa', 'total_credit_hours')
    search_fields = ('student__roll_number',)
    autocomplete_fields = ('student', 'semester')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
