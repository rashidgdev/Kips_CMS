"""
Attaches convenience role/profile context to each request.

This middleware only sets context for views/templates to read - it is
NOT the authorization mechanism. Use `apps.common.permissions` for that.
"""
from django.shortcuts import redirect


class RoleContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.role = None
        request._cached_profile = None

        if request.user.is_authenticated:
            request.role = request.user.role

        return self.get_response(request)


class ForcePasswordChangeMiddleware:
    """Redirects any authenticated user with `must_change_password=True` to
    the change-password page until they set their own. Every account created
    via Administration - individually or via bulk Excel import - starts with
    a system-generated temporary password and this flag set."""

    EXEMPT_PREFIXES = ('/static/', '/media/')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and getattr(request.user, 'must_change_password', False):
            from django.urls import reverse

            change_url = reverse('accounts:password-change')
            logout_url = reverse('accounts:logout')
            if request.path not in (change_url, logout_url) and not request.path.startswith(
                self.EXEMPT_PREFIXES
            ):
                return redirect(change_url)

        return self.get_response(request)


def get_profile(request):
    """Lazily resolve and cache the role-specific profile for the logged in user."""
    if getattr(request, '_cached_profile', None) is not None:
        return request._cached_profile

    if not request.user.is_authenticated:
        return None

    from apps.accounts.models import Roles

    role = request.user.role
    profile = None
    if role == Roles.STUDENT:
        profile = getattr(request.user, 'student_profile', None)
    elif role in (Roles.TEACHER, Roles.HOD):
        profile = getattr(request.user, 'teacher_profile', None)
    elif role in (Roles.COORDINATOR, Roles.ACCOUNTANT, Roles.ADMIN):
        profile = getattr(request.user, 'staff_profile', None)

    request._cached_profile = profile
    return profile
