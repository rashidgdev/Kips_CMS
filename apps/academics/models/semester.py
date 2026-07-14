from django.db import models
from django.db.models import Q

from apps.common.models import TimeStampedModel

from .program import Program


class Semester(TimeStampedModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='semesters')
    number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=100, blank=True)
    academic_year = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ['program', 'number']
        unique_together = ('program', 'number', 'academic_year')
        constraints = [
            models.UniqueConstraint(
                fields=['program'],
                condition=Q(is_current=True),
                name='unique_current_semester_per_program',
                violation_error_message=(
                    'This program already has a current semester. '
                    'Edit the existing one to unmark it as current first.'
                ),
            )
        ]

    def __str__(self):
        return f'{self.program.code} - Semester {self.number} ({self.academic_year})'
