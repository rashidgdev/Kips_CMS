from django import forms

from apps.common.forms import TailwindFormMixin

from .models import Course, CourseOffering, Enrollment, Program, Semester


class ProgramForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'code', 'department', 'total_semesters', 'degree_level', 'is_active']


class SemesterForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['program', 'number', 'name', 'academic_year', 'start_date', 'end_date', 'is_current']


class CourseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = ['program', 'code', 'title', 'credit_hours', 'semester_number', 'course_type', 'is_active']


class CourseOfferingForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = CourseOffering
        fields = ['course', 'semester', 'teacher', 'section', 'max_seats', 'is_active']


class EnrollmentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course_offering', 'status']
