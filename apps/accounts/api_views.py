from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.api_generic import RoleScopedModelViewSet
from apps.common.api_permissions import HasRole, resolve_profile

from .forms import (
    ProfilePhotoForm,
    StaffCreateForm,
    StaffProfileEditForm,
    StudentCreateForm,
    StudentProfileEditForm,
    TeacherCreateForm,
    TeacherProfileEditForm,
)
from .models import Department, Roles, StaffProfile, StudentProfile, TeacherProfile, User
from .serializers import DepartmentSerializer, PersonSerializer
from .services import filter_people

# Matches views.py's STAFF_MANAGEMENT_ROLES - kept as a local tuple here too
# so this file stays readable without cross-importing views.py.
STAFF_MANAGEMENT_ROLES = (Roles.COORDINATOR, Roles.ADMIN)


class DepartmentViewSet(RoleScopedModelViewSet):
    queryset = Department.objects.select_related('hod')
    serializer_class = DepartmentSerializer
    allowed_roles = STAFF_MANAGEMENT_ROLES


# --- Identity --------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """The mobile app's equivalent of apps/common/context_processors.py's
    role_context() - who's logged in, their role, and role-specific profile
    fields, so the client can build its own role-based navigation the same
    way NAV_CONFIG drives the web nav. must_change_password is included so
    the mobile app can route to a change-password screen first, mirroring
    ForcePasswordChangeMiddleware's web behavior at the client level."""
    user = request.user
    data = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.get_full_name(),
        'email': user.email,
        'phone_number': user.phone_number,
        'role': user.role,
        'role_display': user.get_role_display(),
        'is_superuser': user.is_superuser,
        'must_change_password': user.must_change_password,
        'photo_url': request.build_absolute_uri(user.photo.url) if user.photo else None,
        'profile': None,
    }

    profile = resolve_profile(user)
    if profile is not None:
        if user.role == Roles.STUDENT:
            data['profile'] = {
                'id': profile.pk,
                'roll_number': profile.roll_number,
                'program_id': profile.program_id,
                'program': str(profile.program) if profile.program_id else None,
                'current_semester_id': profile.current_semester_id,
                'current_semester': str(profile.current_semester) if profile.current_semester_id else None,
                'status': profile.status,
            }
        elif user.role in (Roles.TEACHER, Roles.HOD):
            data['profile'] = {
                'id': profile.pk,
                'employee_id': profile.employee_id,
                'department_id': profile.department_id,
                'department': profile.department.name if profile.department_id else None,
                'designation': profile.designation,
                'employment_status': profile.employment_status,
            }
        else:
            data['profile'] = {'id': profile.pk, 'employee_id': profile.employee_id}

    return Response(data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_my_photo(request):
    """JSON-adjacent equivalent of apps/accounts/views.py::profile's POST
    branch - same ProfilePhotoForm, so the same image validation applies.
    Expects multipart/form-data with a `photo` file field."""
    form = ProfilePhotoForm(request.data, request.FILES, instance=request.user)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    form.save()
    return Response({'photo_url': request.build_absolute_uri(request.user.photo.url) if request.user.photo else None})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """JSON equivalent of apps/accounts/views.py::ChangePasswordView - same
    Django PasswordChangeForm, so validation (old-password check, new
    password strength/match rules) is identical to the web flow."""
    form = PasswordChangeForm(user=request.user, data=request.data)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    form.save()
    update_session_auth_hash(request, request.user)
    if request.user.must_change_password:
        request.user.must_change_password = False
        request.user.save(update_fields=['must_change_password'])
    return Response({'detail': 'Password changed.'})


# --- People management -------------------------------------------------

class PeopleListAPIView(generics.ListAPIView):
    """JSON equivalent of apps/accounts/views.py::people_directory - same
    role/department/search filters, via the shared services.filter_people()."""
    serializer_class = PersonSerializer
    permission_classes = [HasRole.for_roles(*STAFF_MANAGEMENT_ROLES)]

    def get_queryset(self):
        params = self.request.query_params
        return filter_people(
            role=params.get('role', ''),
            department=params.get('department', ''),
            query=params.get('q', '').strip(),
        )


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*STAFF_MANAGEMENT_ROLES)])
def student_create(request):
    form = StudentCreateForm(request.data, request.FILES)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    profile, temp_password = form.save()
    return Response(
        {
            'id': profile.pk, 'user_id': profile.user_id, 'roll_number': profile.roll_number,
            'username': profile.user.username, 'temp_password': temp_password,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET', 'PATCH', 'PUT'])
@permission_classes([HasRole.for_roles(*STAFF_MANAGEMENT_ROLES)])
def student_update(request, profile_id):
    profile = get_object_or_404(StudentProfile, pk=profile_id)
    if request.method == 'GET':
        # Prefill data for the edit form (StudentProfileEditForm's own fields
        # only) - added alongside the mobile app so an edit screen can show
        # current values instead of blank pickers that would silently wipe
        # them on submit.
        return Response({
            'id': profile.pk,
            'program': profile.program_id, 'program_label': str(profile.program),
            'current_semester': profile.current_semester_id,
            'current_semester_label': str(profile.current_semester) if profile.current_semester_id else None,
            'status': profile.status,
        })
    form = StudentProfileEditForm(request.data, instance=profile)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    form.save()
    return Response({'id': profile.pk, 'status': profile.status})


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*STAFF_MANAGEMENT_ROLES)])
def teacher_create(request):
    form = TeacherCreateForm(request.data, request.FILES)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    profile, temp_password = form.save()
    return Response(
        {
            'id': profile.pk, 'user_id': profile.user_id, 'employee_id': profile.employee_id,
            'username': profile.user.username, 'temp_password': temp_password,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET', 'PATCH', 'PUT'])
@permission_classes([HasRole.for_roles(*STAFF_MANAGEMENT_ROLES)])
def teacher_update(request, profile_id):
    profile = get_object_or_404(TeacherProfile, pk=profile_id)
    if request.method == 'GET':
        return Response({
            'id': profile.pk,
            'department': profile.department_id, 'department_label': str(profile.department),
            'designation': profile.designation,
            'per_lecture_rate': profile.per_lecture_rate,
            'employment_status': profile.employment_status,
        })
    form = TeacherProfileEditForm(request.data, instance=profile)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    form.save()
    return Response({'id': profile.pk, 'employment_status': profile.employment_status})


@api_view(['POST'])
@permission_classes([HasRole.for_roles(Roles.ADMIN)])
def staff_create(request):
    form = StaffCreateForm(request.data, request.FILES)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    profile, temp_password = form.save()
    return Response(
        {
            'id': profile.pk, 'user_id': profile.user_id, 'employee_id': profile.employee_id,
            'username': profile.user.username, 'temp_password': temp_password,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(['GET', 'PATCH', 'PUT'])
@permission_classes([HasRole.for_roles(Roles.ADMIN)])
def staff_update(request, profile_id):
    profile = get_object_or_404(StaffProfile, pk=profile_id)
    if request.method == 'GET':
        return Response({'id': profile.pk, 'notes': profile.notes})
    form = StaffProfileEditForm(request.data, instance=profile)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    form.save()
    return Response({'id': profile.pk, 'notes': profile.notes})


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*STAFF_MANAGEMENT_ROLES)])
def toggle_active(request, user_id):
    """Mirrors views.py::toggle_active's privilege-escalation guard exactly:
    only a College Administrator can activate/deactivate a Coordinator/
    Accountant/Admin account."""
    person = get_object_or_404(User, pk=user_id)
    if person.role in (Roles.COORDINATOR, Roles.ACCOUNTANT, Roles.ADMIN) and request.user.role != Roles.ADMIN:
        return Response(
            {'detail': 'Only a College Administrator can activate/deactivate staff accounts.'},
            status=status.HTTP_403_FORBIDDEN,
        )
    person.is_active = not person.is_active
    person.save(update_fields=['is_active'])
    return Response({'id': person.pk, 'is_active': person.is_active})
