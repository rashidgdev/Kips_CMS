from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.accounts.models import Roles, StudentProfile
from apps.common.api_generic import RoleScopedModelViewSet
from apps.common.api_permissions import HasRole

from .models import Course, CourseOffering, Enrollment, Program, Semester
from .serializers import (
    CourseOfferingSerializer,
    CourseSerializer,
    EnrollmentSerializer,
    ProgramSerializer,
    SemesterSerializer,
)
from .services import bulk_enroll_by_offering, bulk_enroll_by_student

STAFF_ROLES = (Roles.COORDINATOR, Roles.ADMIN)


class ProgramViewSet(RoleScopedModelViewSet):
    queryset = Program.objects.select_related('department')
    serializer_class = ProgramSerializer
    allowed_roles = STAFF_ROLES


class SemesterViewSet(RoleScopedModelViewSet):
    queryset = Semester.objects.select_related('program')
    serializer_class = SemesterSerializer
    allowed_roles = STAFF_ROLES


class CourseViewSet(RoleScopedModelViewSet):
    queryset = Course.objects.select_related('program')
    serializer_class = CourseSerializer
    allowed_roles = STAFF_ROLES


class CourseOfferingViewSet(RoleScopedModelViewSet):
    queryset = CourseOffering.objects.select_related('course', 'semester', 'teacher__user', 'assigned_by')
    serializer_class = CourseOfferingSerializer
    allowed_roles = STAFF_ROLES

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class EnrollmentViewSet(RoleScopedModelViewSet):
    queryset = Enrollment.objects.select_related(
        'student__user', 'course_offering__course', 'course_offering__semester'
    )
    serializer_class = EnrollmentSerializer
    allowed_roles = STAFF_ROLES


@api_view(['GET', 'POST'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def enroll_by_offering_api(request):
    """Pick one course offering, then enroll many students into it at once -
    JSON equivalent of views.py::enroll_by_offering. GET ?offering=<id>
    returns that offering's program-matched active students plus which are
    already enrolled; POST {"offering": <id>, "student_ids": [...]} enrolls
    the rest (already-enrolled ids are silently skipped, not an error)."""
    offering_id = request.query_params.get('offering') or request.data.get('offering')
    if not offering_id:
        return Response({'detail': 'offering is required.'}, status=400)
    offering = get_object_or_404(CourseOffering, pk=offering_id)

    if request.method == 'POST':
        student_ids = {int(sid) for sid in request.data.get('student_ids', [])}
        if not student_ids:
            return Response({'detail': 'Select at least one student to enroll.'}, status=400)
        enrolled_count = bulk_enroll_by_offering(offering, student_ids)
        return Response({'enrolled_count': enrolled_count}, status=201)

    already_enrolled_ids = set(offering.enrollments.values_list('student_id', flat=True))
    students = StudentProfile.objects.filter(
        program=offering.course.program, status=StudentProfile.Status.ACTIVE
    ).select_related('user').order_by('roll_number')
    return Response({
        'offering': CourseOfferingSerializer(offering).data,
        'students': [
            {
                'id': s.pk, 'roll_number': s.roll_number, 'name': s.user.get_full_name(),
                'already_enrolled': s.pk in already_enrolled_ids,
            }
            for s in students
        ],
    })


@api_view(['GET', 'POST'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def enroll_by_student_api(request):
    """Pick one student, then enroll them into many course offerings at once
    - JSON equivalent of views.py::enroll_by_student. GET ?student=<id>
    returns that student's program-matched active offerings plus which
    they're already enrolled in; POST {"student": <id>, "offering_ids": [...]}
    enrolls the rest (already-enrolled ids are silently skipped)."""
    student_id = request.query_params.get('student') or request.data.get('student')
    if not student_id:
        return Response({'detail': 'student is required.'}, status=400)
    student = get_object_or_404(StudentProfile, pk=student_id)

    if request.method == 'POST':
        offering_ids = {int(oid) for oid in request.data.get('offering_ids', [])}
        if not offering_ids:
            return Response({'detail': 'Select at least one course offering.'}, status=400)
        enrolled_count = bulk_enroll_by_student(student, offering_ids)
        return Response({'enrolled_count': enrolled_count}, status=201)

    already_enrolled_ids = set(student.enrollments.values_list('course_offering_id', flat=True))
    offerings = CourseOffering.objects.filter(
        course__program=student.program, is_active=True
    ).select_related('course', 'semester').order_by('-semester__is_current', 'semester', 'course')
    return Response({
        'student': {'id': student.pk, 'roll_number': student.roll_number, 'name': student.user.get_full_name()},
        'offerings': [
            {
                'id': o.pk, 'course': str(o.course), 'semester': str(o.semester),
                'already_enrolled': o.pk in already_enrolled_ids,
            }
            for o in offerings
        ],
    })
