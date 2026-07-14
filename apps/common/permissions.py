"""
Central role-based authorization gate.

Every view that must be restricted to specific roles uses `role_required`
(function views) or `RoleRequiredMixin` (class-based views) from here,
instead of repeating `if request.user.role != ...` checks per view.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Restrict a view to users whose `role` is in `roles`.

    Superusers always pass, so `/admin/`-created staff accounts and
    `createsuperuser` accounts are never locked out.
    """

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.is_superuser or request.user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return wrapped
    return decorator


class RoleRequiredMixin:
    """Class-based-view equivalent of `role_required`.

    Set `allowed_roles = (Roles.TEACHER, Roles.HOD)` on the view.
    """

    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if request.user.is_superuser or request.user.role in self.allowed_roles:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied
