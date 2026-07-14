from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel

from .user import Roles


class Department(TimeStampedModel):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    hod = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': Roles.HOD},
        related_name='departments_headed',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.code} - {self.name}'
