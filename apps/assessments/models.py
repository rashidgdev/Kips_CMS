from django.conf import settings
from django.db import models

from apps.academics.models import CourseOffering, Semester
from apps.common.models import TimeStampedModel


class AssessmentCategory(TimeStampedModel):
    """Lookup table (quiz/assignment/presentation/midterm/final) - weight is configurable per course."""

    name = models.CharField(max_length=50, unique=True)
    default_weight_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Assessment categories'

    def __str__(self):
        return self.name


class Assessment(TimeStampedModel):
    course_offering = models.ForeignKey(
        CourseOffering, on_delete=models.CASCADE, related_name='assessments'
    )
    category = models.ForeignKey(
        AssessmentCategory, on_delete=models.PROTECT, related_name='assessments'
    )
    title = models.CharField(max_length=150)
    total_marks = models.DecimalField(max_digits=6, decimal_places=2)
    weight_percent = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+'
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.course_offering} - {self.title}'


class Mark(TimeStampedModel):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey(
        'accounts.StudentProfile', on_delete=models.CASCADE, related_name='marks'
    )
    obtained_marks = models.DecimalField(max_digits=6, decimal_places=2)
    remarks = models.CharField(max_length=255, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+'
    )
    graded_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['assessment']
        unique_together = ('assessment', 'student')

    def __str__(self):
        return f'{self.student.roll_number} - {self.assessment} - {self.obtained_marks}'


class CourseResult(TimeStampedModel):
    """Cached aggregate, recalculated whenever a Mark changes - see signals.py."""

    student = models.ForeignKey(
        'accounts.StudentProfile', on_delete=models.CASCADE, related_name='course_results'
    )
    course_offering = models.ForeignKey(
        CourseOffering, on_delete=models.CASCADE, related_name='results'
    )
    total_obtained = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_possible = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade_letter = models.CharField(max_length=2, blank=True)
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['course_offering']
        unique_together = ('student', 'course_offering')

    def __str__(self):
        return f'{self.student.roll_number} - {self.course_offering}'


class SemesterGPA(TimeStampedModel):
    """Cached aggregate, recalculated whenever a CourseResult in the semester changes."""

    student = models.ForeignKey(
        'accounts.StudentProfile', on_delete=models.CASCADE, related_name='semester_gpas'
    )
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='student_gpas')
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_credit_hours = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['-semester__number']
        unique_together = ('student', 'semester')

    def __str__(self):
        return f'{self.student.roll_number} - {self.semester} - GPA {self.gpa}'
