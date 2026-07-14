from django.db import models

from apps.common.models import TimeStampedModel


class Program(TimeStampedModel):
    class DegreeLevel(models.TextChoices):
        BACHELORS = 'bachelors', "Bachelor's"
        ASSOCIATE = 'associate', 'Associate'
        DIPLOMA = 'diploma', 'Diploma'

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        'accounts.Department', on_delete=models.PROTECT, related_name='programs'
    )
    total_semesters = models.PositiveSmallIntegerField(default=8)
    degree_level = models.CharField(
        max_length=20, choices=DegreeLevel.choices, default=DegreeLevel.BACHELORS
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.code} - {self.name}'
