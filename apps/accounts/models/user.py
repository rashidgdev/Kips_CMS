from django.contrib.auth.models import AbstractUser
from django.db import models


class Roles(models.TextChoices):
    STUDENT = 'student', 'Student'
    TEACHER = 'teacher', 'Teacher'
    HOD = 'hod', 'Head of Department'
    COORDINATOR = 'coordinator', 'Campus Coordinator'
    ACCOUNTANT = 'accountant', 'Accountant'
    ADMIN = 'admin', 'College Administrator'


class User(AbstractUser):
    role = models.CharField(max_length=20, choices=Roles.choices)
    phone_number = models.CharField(max_length=20, blank=True)
    must_change_password = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'
