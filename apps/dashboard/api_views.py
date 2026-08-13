from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Roles
from apps.common.api_permissions import resolve_profile

from . import services as dashboard_services


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_me(request):
    """One endpoint, payload shaped by the logged-in user's role - mirrors
    dashboard_redirect() dispatching to a different template per role,
    just returning JSON instead. Reuses the exact same services.py
    functions the Django dashboard views call, so the numbers can never
    drift between web and mobile."""
    role = request.user.role
    profile = resolve_profile(request.user)

    if role == Roles.STUDENT:
        data = dashboard_services.get_student_dashboard_data(profile)
        return Response({
            'role': role,
            'enrollments': [
                {
                    'id': e.pk,
                    'course': str(e.course_offering.course),
                    'teacher': e.course_offering.teacher.user.get_full_name(),
                    'status': e.status,
                }
                for e in data['enrollments']
            ],
            'cgpa': data['cgpa'],
            'current_semester_gpa': data['current_gpa'].gpa if data['current_gpa'] else None,
            'overall_attendance_percent': data['overall_attendance'],
        })

    if role in (Roles.TEACHER, Roles.HOD):
        teacher_data = dashboard_services.get_teacher_dashboard_data(profile)
        payload = {
            'role': role,
            'offerings': [
                {'id': o.pk, 'course': str(o.course), 'semester': str(o.semester), 'section': o.section}
                for o in teacher_data['offerings']
            ],
            'todays_classes': [
                {
                    'id': t.pk,
                    'course': str(t.course_offering.course),
                    'room': str(t.room),
                    'start_time': t.time_slot.start_time_display,
                    'end_time': t.time_slot.end_time_display,
                }
                for t in teacher_data['todays_classes']
            ],
        }
        if role == Roles.HOD:
            hod_data = dashboard_services.get_hod_dashboard_data(profile)
            payload['department'] = str(hod_data['department']) if hod_data['department'] else None
        return Response(payload)

    if role == Roles.COORDINATOR:
        return Response({'role': role, **dashboard_services.get_coordinator_dashboard_data()})

    if role == Roles.ACCOUNTANT:
        return Response({'role': role, **dashboard_services.get_accountant_dashboard_data()})

    if role == Roles.ADMIN:
        return Response({'role': role, **dashboard_services.get_admin_dashboard_data()})

    return Response({'role': role})
