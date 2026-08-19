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
            'attendance_by_course': [
                {
                    'course': str(row['course_offering'].course),
                    'delivered': row['delivered'], 'attended': row['attended'], 'absent': row['absent'],
                    'percentage': row['percentage'], 'is_shortage': row['is_shortage'],
                }
                for row in data['attendance_rows']
            ],
            'marks_by_course': [
                {
                    'course': str(row['course_offering'].course),
                    'total_obtained': row['total_obtained'], 'total_possible': row['total_possible'],
                    'percentage': row['percentage'], 'grade_letter': row['grade_letter'],
                }
                for row in data['marks_rows']
            ],
            'fee_total_due': data['fee_overview']['total_due'] if data['fee_overview'] else None,
            'fee_total_paid': data['fee_overview']['total_paid'] if data['fee_overview'] else None,
            'fee_total_outstanding': data['fee_overview']['total_outstanding'] if data['fee_overview'] else None,
            'todays_classes': [
                {
                    'id': t.pk,
                    'course': str(t.course_offering.course),
                    'room': str(t.room),
                    'start_time': t.time_slot.start_time_display,
                    'end_time': t.time_slot.end_time_display,
                }
                for t in data['todays_classes']
            ],
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
            'student_count': teacher_data['student_count'],
            'unverified_daybook_count': teacher_data['unverified_count'],
            'workload_this_month': {
                'total_lectures': teacher_data['workload']['total_lectures'],
                'verified_lectures': teacher_data['workload']['verified_lectures'],
                'unverified_lectures': teacher_data['workload']['unverified_lectures'],
                'total_amount': teacher_data['workload']['total_amount'],
            } if teacher_data['workload'] else None,
        }
        if role == Roles.HOD:
            hod_data = dashboard_services.get_hod_dashboard_data(profile)
            payload['department'] = str(hod_data['department']) if hod_data['department'] else None
            payload['department_teacher_count'] = hod_data['department_teacher_count']
            payload['department_offering_count'] = hod_data['department_offering_count']
        return Response(payload)

    if role == Roles.COORDINATOR:
        return Response({'role': role, **dashboard_services.get_coordinator_dashboard_data()})

    if role == Roles.ACCOUNTANT:
        data = dashboard_services.get_accountant_dashboard_data()
        data['recent_payments'] = _serialize_recent_payments(data['recent_payments'])
        return Response({'role': role, **data})

    if role == Roles.ADMIN:
        data = dashboard_services.get_admin_dashboard_data()
        data['accountant']['recent_payments'] = _serialize_recent_payments(data['accountant']['recent_payments'])
        return Response({'role': role, **data})

    return Response({'role': role})


def _serialize_recent_payments(payments):
    """Payment model instances (kept raw in the dashboard service for the
    web templates, which read them via dot-notation) reshaped into
    JSON-safe dicts for the API response."""
    return [
        {
            'id': p.pk,
            'student': p.fee_item.student.user.get_full_name(),
            'category': str(p.fee_item.category),
            'amount_paid': p.amount_paid,
            'payment_date': p.payment_date,
        }
        for p in payments
    ]
