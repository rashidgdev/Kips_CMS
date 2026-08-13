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


def resolve_profile(user):
    """Like apps.common.middleware.get_profile(), but resolves fresh from a
    `User` instance instead of reading request._cached_profile. That cache
    is populated by RoleContextMiddleware, which runs *before* DRF's own
    authentication resolves request.user for token-based auth (JWT) - for a
    JWT request there's no session, so the middleware sees an AnonymousUser
    and caches nothing/wrong, while DRF only authenticates the real user
    later, inside the view. Session-authenticated requests aren't affected
    (the session user is already resolved by middleware time), but any API
    code must use this helper, not the middleware one, to work correctly
    for both auth methods."""
    from apps.accounts.models import Roles

    role = user.role
    if role == Roles.STUDENT:
        return getattr(user, 'student_profile', None)
    if role in (Roles.TEACHER, Roles.HOD):
        return getattr(user, 'teacher_profile', None)
    if role in (Roles.COORDINATOR, Roles.ACCOUNTANT, Roles.ADMIN):
        return getattr(user, 'staff_profile', None)
    return None


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

        user = request.user
        if user.is_superuser or user.role in self.staff_roles:
            return True
        if user.role != Roles.STUDENT:
            return False
        profile = resolve_profile(user)
        if profile is None:
            return False
        return view.get_owner_profile_id(obj) == profile.pk

    @classmethod
    def for_roles(cls, *staff_roles):
        return type('IsOwnerOrRolesScoped', (cls,), {'staff_roles': staff_roles})
