"""
Attaches convenience role/profile context to each request.

This middleware only sets context for views/templates to read - it is
NOT the authorization mechanism. Use `apps.common.permissions` for that.
"""
from django.shortcuts import redirect


class JWTBridgeMiddleware:
    """Lets a JWT `Authorization: Bearer <token>` header authenticate plain
    Django views (e.g. the PDF/CSV/Excel export views), not just DRF views.

    DRF's JWTAuthentication only runs inside DRF's own view dispatch - a
    plain `@role_required`/`@login_required` view reads `request.user`,
    which `AuthenticationMiddleware` (just before this one) resolves from
    the session only, so a JWT-only mobile client would silently get
    treated as anonymous and redirected to the login page instead of
    getting the file it asked for.

    This only acts when the session left `request.user` anonymous AND a
    Bearer header is present, so it's a no-op for every session-authenticated
    web request - that path never reaches the JWT branch. Placed *before*
    RoleContextMiddleware so the profile it caches is resolved against the
    real (not anonymous) user, matching apps.common.api_permissions.
    resolve_profile's reasoning for the same problem on the DRF side."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Bearer '):
                from rest_framework_simplejwt.authentication import JWTAuthentication
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

                try:
                    result = JWTAuthentication().authenticate(request)
                except (InvalidToken, TokenError):
                    result = None
                if result is not None:
                    request.user, _ = result

        return self.get_response(request)


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
    a system-generated temporary password and this flag set.

    `/api/` is exempt for the same reason `/static/`/`/media/` are: an HTML
    redirect makes no sense for a JSON client. The mobile app reads
    `must_change_password` from GET /api/v1/accounts/me/ and routes to its
    own change-password screen itself (see mobile/src/app/(auth)/
    change-password.tsx) - this middleware redirecting the API's own /me/
    call would make that flag impossible to ever read. This only became
    reachable once JWTBridgeMiddleware (just above) started resolving
    `request.user` for JWT-only requests too; before that, this middleware
    always saw AnonymousUser for API calls and never redirected them."""

    EXEMPT_PREFIXES = ('/static/', '/media/', '/api/')

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
