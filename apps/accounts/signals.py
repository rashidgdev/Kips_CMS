from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models.user import Roles


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_role_group(sender, instance, created, **kwargs):
    """Keep each user's Django Group in sync with their `role`.

    This enables `has_perm()`/`@permission_required` for fine-grained,
    per-model permissions later, layered on top of the coarse role field
    that drives routing/middleware.
    """
    if not instance.role:
        return

    group_name = Roles(instance.role).label
    group, _ = Group.objects.get_or_create(name=group_name)

    role_group_names = [role.label for role in Roles if role.label != group_name]
    instance.groups.remove(*Group.objects.filter(name__in=role_group_names))
    instance.groups.add(group)
