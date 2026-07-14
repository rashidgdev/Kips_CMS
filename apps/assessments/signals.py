from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Mark
from .services import recalculate_course_result


def _recalc_for_mark(mark):
    recalculate_course_result(mark.student, mark.assessment.course_offering)


@receiver(post_save, sender=Mark)
def mark_saved(sender, instance, **kwargs):
    _recalc_for_mark(instance)


@receiver(post_delete, sender=Mark)
def mark_deleted(sender, instance, **kwargs):
    _recalc_for_mark(instance)
