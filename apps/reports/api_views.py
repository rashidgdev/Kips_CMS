from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.academics.models import CourseOffering, Semester
from apps.accounts.models import Roles, StudentProfile
from apps.common.api_permissions import HasRole, resolve_profile

from .services import get_academic_report, get_attendance_report, get_merit_list, get_student_progress_report

STAFF_ROLES = (Roles.COORDINATOR, Roles.ADMIN, Roles.TEACHER, Roles.HOD)


def _scoped_offerings(request):
    """Same scoping as reports/views.py: Teacher/HOD only their own offerings,
    Coordinator/Admin any active offering."""
    if request.user.role in (Roles.TEACHER, Roles.HOD):
        profile = resolve_profile(request.user)
        return CourseOffering.objects.filter(teacher=profile, is_active=True).select_related('course', 'semester')
    return CourseOffering.objects.filter(is_active=True).select_related('course', 'semester')


def _serialize_attendance_rows(rows):
    return [
        {
            'student_id': r['student'].pk, 'roll_number': r['student'].roll_number,
            'name': r['student'].user.get_full_name(), 'delivered': r['delivered'],
            'attended': r['attended'], 'absent': r['absent'], 'percentage': r['percentage'],
            'is_shortage': r['is_shortage'],
        }
        for r in rows
    ]


def _serialize_academic_rows(rows):
    return [
        {
            'student_id': r['student'].pk, 'roll_number': r['student'].roll_number,
            'name': r['student'].user.get_full_name(), 'total_obtained': r['total_obtained'],
            'total_possible': r['total_possible'], 'percentage': r['percentage'],
            'grade_letter': r['grade_letter'],
        }
        for r in rows
    ]


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def attendance_report_api(request):
    offering_id = request.query_params.get('course_offering')
    if not offering_id:
        return Response({'detail': 'course_offering query param is required.'}, status=status.HTTP_400_BAD_REQUEST)
    offering = get_object_or_404(_scoped_offerings(request), pk=offering_id)
    rows = get_attendance_report(offering)
    return Response({'course_offering': str(offering), 'rows': _serialize_attendance_rows(rows)})


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def academic_report_api(request):
    offering_id = request.query_params.get('course_offering')
    if not offering_id:
        return Response({'detail': 'course_offering query param is required.'}, status=status.HTTP_400_BAD_REQUEST)
    offering = get_object_or_404(_scoped_offerings(request), pk=offering_id)
    rows = get_academic_report(offering)
    return Response({'course_offering': str(offering), 'rows': _serialize_academic_rows(rows)})


@api_view(['GET'])
@permission_classes([HasRole.for_roles(Roles.COORDINATOR, Roles.ADMIN)])
def merit_list_api(request):
    semester_id = request.query_params.get('semester')
    if not semester_id:
        return Response({'detail': 'semester query param is required.'}, status=status.HTTP_400_BAD_REQUEST)
    semester = get_object_or_404(Semester, pk=semester_id)
    rows = get_merit_list(semester)
    return Response({
        'semester': str(semester),
        'rows': [
            {
                'rank': i, 'student_id': g.student_id, 'roll_number': g.student.roll_number,
                'name': g.student.user.get_full_name(), 'gpa': g.gpa, 'total_credit_hours': g.total_credit_hours,
            }
            for i, g in enumerate(rows, start=1)
        ],
    })


class _StudentBriefSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = StudentProfile
        fields = ['id', 'roll_number', 'name']


class ProgressStudentsAPIView(generics.ListAPIView):
    """Staff-facing search used to pick a student before opening their
    progress report - mirrors reports/views.py::progress_students."""
    serializer_class = _StudentBriefSerializer
    permission_classes = [HasRole.for_roles(*STAFF_ROLES)]

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()
        students = StudentProfile.objects.select_related('user').order_by('roll_number')
        if query:
            students = students.filter(
                Q(roll_number__icontains=query)
                | Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__username__icontains=query)
            )
        return students


def _resolve_progress_student(request, student_id):
    """Mirrors reports/views.py::_progress_report_student's ownership check
    exactly: a student may only open their own report; staff may open any."""
    student = get_object_or_404(StudentProfile.objects.select_related('user', 'program'), pk=student_id)
    is_owner = request.user.role == Roles.STUDENT and resolve_profile(request.user) is not None and \
        resolve_profile(request.user).pk == student.pk
    is_staff = request.user.role in STAFF_ROLES
    if not (is_owner or is_staff):
        raise PermissionDenied('You do not have permission to view this student\'s progress report.')
    return student


@api_view(['GET'])
@permission_classes([HasRole.for_roles(Roles.STUDENT, *STAFF_ROLES)])
def progress_report_api(request, student_id):
    student = _resolve_progress_student(request, student_id)
    semesters = Semester.objects.filter(program=student.program).order_by('-number')
    semester_id = request.query_params.get('semester') or student.current_semester_id or (
        semesters.first().pk if semesters.exists() else None
    )
    if not semester_id:
        return Response({
            'student_id': student.pk, 'roll_number': student.roll_number,
            'semesters': [{'id': s.pk, 'label': str(s)} for s in semesters], 'report': None,
        })

    semester = get_object_or_404(Semester, pk=semester_id)
    report = get_student_progress_report(student, semester)
    return Response({
        'student_id': student.pk,
        'roll_number': student.roll_number,
        'name': student.user.get_full_name(),
        'semesters': [{'id': s.pk, 'label': str(s)} for s in semesters],
        'selected_semester_id': semester.pk,
        'report': {
            'semester': str(report['semester']),
            'attendance_overall': report['attendance_overall'],
            'category_breakdown': report['category_breakdown'],
            'course_rows': [
                {
                    'offering_id': row['offering'].pk,
                    'course': str(row['offering'].course),
                    'attendance_percentage': row['attendance']['percentage'],
                    'total_obtained': row['result'].total_obtained if row['result'] else None,
                    'total_possible': row['result'].total_possible if row['result'] else None,
                    'grade_letter': row['result'].grade_letter if row['result'] else None,
                }
                for row in report['course_rows']
            ],
            'semester_gpa': report['semester_gpa'].gpa if report['semester_gpa'] else None,
        },
    })
