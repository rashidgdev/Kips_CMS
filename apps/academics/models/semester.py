from django.db import models

from apps.common.models import TimeStampedModel

from .program import Program


class Semester(TimeStampedModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='semesters')
    number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=100, blank=True)
    academic_year = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(
        default=False,
        help_text=(
            'Whether this semester is actively running right now. More than one semester of the '
            'same program can be current at once - e.g. Semester 3 and Semester 5 both running '
            'concurrently for different cohorts of the same program.'
        ),
    )

    class Meta:
        ordering = ['program', 'number']
        unique_together = ('program', 'number', 'academic_year')

    def __str__(self):
        return f'{self.program.code} - Semester {self.number} ({self.academic_year})'
