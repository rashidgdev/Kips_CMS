"""
DRF permission classes mirroring apps/common/permissions.py's role gate
exactly, so API endpoints enforce the identical rules the Django template
views already do (role_required / RoleRequiredMixin: superuser always
passes, else request.user.role must be one of the allowed roles).
"""
from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """Base class - use `HasRole.for_roles(*roles)` to get a permission
    class parametrized with the allowed roles, e.g.:

        permission_classes = [HasRole.for_roles(Roles.COORDINATOR, Roles.ADMIN)]
    """
    allowed_roles = ()
    message = 'You do not have permission to perform this action.'

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        return user.is_superuser or user.role in self.allowed_roles

    @classmethod
    def for_roles(cls, *roles):
        return type('HasRoleScoped', (cls,), {'allowed_roles': roles})


class IsOwnerOrRoles(BasePermission):
    """Mirrors the ownership-check idiom used by finance's challan_pdf and
    reports' progress_report views: either the requester IS the student who
    owns the object, or they hold one of `staff_roles`. The view must
    implement `get_owner_profile_id(self, obj)` returning the StudentProfile
    pk that owns `obj` - use `IsOwnerOrRoles.for_roles(*staff_roles)`.
    """
    staff_roles = ()
    message = 'You do not have permission to access this record.'

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        from apps.accounts.models import Roles
        from apps.common.middleware import get_profile

        user = request.user
        if user.is_superuser or user.role in self.staff_roles:
            return True
        if user.role != Roles.STUDENT:
            return False
        profile = get_profile(request)
        if profile is None:
            return False
        return view.get_owner_profile_id(obj) == profile.pk

    @classmethod
    def for_roles(cls, *staff_roles):
        return type('IsOwnerOrRolesScoped', (cls,), {'staff_roles': staff_roles})
