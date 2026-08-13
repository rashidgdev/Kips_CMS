from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.academics.models import CourseOffering, Enrollment
from apps.accounts.models import Roles
from apps.common.api_permissions import HasRole, resolve_profile

from .forms import LectureSessionForm
from .models import AttendanceRecord, LectureSession
from .serializers import LectureSessionSerializer
from .services import get_student_course_stats, get_student_overview, mark_attendance_bulk

TEACHER_ROLES = (Roles.TEACHER, Roles.HOD)


def _get_own_offering(request, offering_id):
    profile = resolve_profile(request.user)
    return get_object_or_404(CourseOffering, pk=offering_id, teacher=profile)


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*TEACHER_ROLES)])
def offering_list_api(request):
    profile = resolve_profile(request.user)
    offerings = profile.course_offerings.select_related('course', 'semester').filter(is_active=True)
    return Response([
        {'id': o.pk, 'course': str(o.course), 'semester': str(o.semester), 'section': o.section}
        for o in offerings
    ])


@api_view(['GET', 'POST'])
@permission_classes([HasRole.for_roles(*TEACHER_ROLES)])
def session_list_api(request, offering_id):
    offering = _get_own_offering(request, offering_id)

    if request.method == 'POST':
        form = LectureSessionForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        session = form.save(commit=False)
        session.course_offering = offering
        session.created_by = request.user
        session.save()
        return Response(LectureSessionSerializer(session).data, status=status.HTTP_201_CREATED)

    sessions = offering.sessions.all()
    return Response(LectureSessionSerializer(sessions, many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([HasRole.for_roles(*TEACHER_ROLES)])
def mark_attendance_api(request, session_id):
    profile = resolve_profile(request.user)
    session = get_object_or_404(LectureSession, pk=session_id, course_offering__teacher=profile)

    enrollments = Enrollment.objects.filter(
        course_offering=session.course_offering, status=Enrollment.Status.ENROLLED
    ).select_related('student__user')

    if request.method == 'POST':
        status_by_student_id = {
            int(sid): value for sid, value in (request.data or {}).get('statuses', {}).items()
        }
        records = mark_attendance_bulk(session, status_by_student_id, marked_by=request.user)
        return Response({'detail': 'Attendance saved.', 'saved_count': len(records)})

    existing = {r.student_id: r.status for r in session.records.all()}
    rows = [
        {
            'student_id': e.student.pk,
            'roll_number': e.student.roll_number,
            'name': e.student.user.get_full_name(),
            'status': existing.get(e.student.pk, AttendanceRecord.Status.PRESENT),
        }
        for e in enrollments
    ]
    return Response({
        'session': LectureSessionSerializer(session).data,
        'status_choices': list(AttendanceRecord.Status.choices),
        'rows': rows,
    })


@api_view(['GET'])
@permission_classes([HasRole.for_roles(Roles.STUDENT)])
def student_overview_api(request):
    profile = resolve_profile(request.user)
    stats = get_student_overview(profile)
    return Response([
        {
            'course_offering_id': s['course_offering'].pk,
            'course': str(s['course_offering'].course),
            'delivered': s['delivered'], 'attended': s['attended'], 'absent': s['absent'],
            'percentage': s['percentage'], 'threshold': s['threshold'], 'is_shortage': s['is_shortage'],
        }
        for s in stats
    ])


@api_view(['GET'])
@permission_classes([HasRole.for_roles(Roles.STUDENT)])
def student_course_detail_api(request, offering_id):
    profile = resolve_profile(request.user)
    offering = get_object_or_404(
        CourseOffering, pk=offering_id, enrollments__student=profile,
        enrollments__status=Enrollment.Status.ENROLLED,
    )
    stat = get_student_course_stats(profile, offering)
    records = AttendanceRecord.objects.filter(session__course_offering=offering, student=profile).select_related('session')
    return Response({
        'course': str(offering.course),
        'delivered': stat['delivered'], 'attended': stat['attended'], 'absent': stat['absent'],
        'percentage': stat['percentage'], 'is_shortage': stat['is_shortage'],
        'records': [
            {'session_id': r.session_id, 'date': r.session.date, 'status': r.status}
            for r in records
        ],
    })
