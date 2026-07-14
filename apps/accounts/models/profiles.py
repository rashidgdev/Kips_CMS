from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel

from .department import Department


class StudentProfile(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        GRADUATED = 'graduated', 'Graduated'
        DROPPED = 'dropped', 'Dropped'
        SUSPENDED = 'suspended', 'Suspended'

    class Gender(models.TextChoices):
        MALE = 'male', 'Male'
        FEMALE = 'female', 'Female'
        OTHER = 'other', 'Other'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile'
    )
    roll_number = models.CharField(max_length=30, unique=True)
    program = models.ForeignKey(
        'academics.Program', on_delete=models.PROTECT, related_name='students'
    )
    current_semester = models.ForeignKey(
        'academics.Semester',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
    )
    admission_date = models.DateField()
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True)
    address = models.TextField(blank=True)
    guardian_name = models.CharField(max_length=150, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    cnic = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ['roll_number']

    def __str__(self):
        return f'{self.roll_number} - {self.user.get_full_name()}'


class TeacherProfile(TimeStampedModel):
    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ON_LEAVE = 'on_leave', 'On Leave'
        LEFT = 'left', 'Left'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher_profile'
    )
    employee_id = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='teachers'
    )
    designation = models.CharField(max_length=100, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    joining_date = models.DateField()
    per_lecture_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    employment_status = models.CharField(
        max_length=20, choices=EmploymentStatus.choices, default=EmploymentStatus.ACTIVE
    )

    class Meta:
        ordering = ['employee_id']

    def __str__(self):
        return f'{self.employee_id} - {self.user.get_full_name()}'


class StaffProfile(TimeStampedModel):
    """Shared profile for Coordinator, Accountant, and Admin roles."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile'
    )
    employee_id = models.CharField(max_length=30, unique=True)
    joining_date = models.DateField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['employee_id']

    def __str__(self):
        return f'{self.employee_id} - {self.user.get_full_name()}'
