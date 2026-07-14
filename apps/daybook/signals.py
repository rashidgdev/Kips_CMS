from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.attendance.models import LectureSession

from .models import DayBookEntry


@receiver(post_save, sender=LectureSession)
def create_daybook_entry(sender, instance, created, **kwargs):
    """Every delivered lecture automatically gets a day book entry to verify."""
    if created:
        DayBookEntry.objects.get_or_create(session=instance)
