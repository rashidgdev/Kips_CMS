from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Department, StaffProfile, StudentProfile, TeacherProfile, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Role', {'fields': ('role', 'phone_number', 'must_change_password')}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role', 'email', 'phone_number')}),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'hod')
    search_fields = ('code', 'name')
    autocomplete_fields = ('hod',)


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'user', 'program', 'current_semester', 'status')
    list_filter = ('program', 'status')
    search_fields = ('roll_number', 'user__first_name', 'user__last_name', 'user__username')
    autocomplete_fields = ('user', 'program', 'current_semester')


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'designation', 'employment_status')
    list_filter = ('department', 'employment_status')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__username')
    autocomplete_fields = ('user', 'department')


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'joining_date')
    search_fields = ('employee_id', 'user__first_name', 'user__last_name', 'user__username')
    autocomplete_fields = ('user',)
