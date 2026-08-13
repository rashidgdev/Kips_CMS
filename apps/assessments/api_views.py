from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.academics.models import CourseOffering, Enrollment
from apps.accounts.models import Roles
from apps.common.api_generic import RoleScopedModelViewSet
from apps.common.api_permissions import HasRole, resolve_profile

from .forms import AssessmentForm
from .models import Assessment, AssessmentCategory, CourseResult, SemesterGPA
from .serializers import AssessmentCategorySerializer, AssessmentSerializer
from .services import enter_marks_bulk, get_cgpa, get_student_course_overview

STAFF_ROLES = (Roles.COORDINATOR, Roles.ADMIN)
TEACHER_ROLES = (Roles.TEACHER, Roles.HOD)


class AssessmentCategoryViewSet(RoleScopedModelViewSet):
    queryset = AssessmentCategory.objects.all()
    serializer_class = AssessmentCategorySerializer
    allowed_roles = STAFF_ROLES


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*TEACHER_ROLES, *STAFF_ROLES)])
def category_options_api(request):
    """Read-only category list for Teacher/HOD - they need this to populate
    the category picker when creating an Assessment, but AssessmentCategory
    management itself (create/edit/delete via AssessmentCategoryViewSet
    above) stays Coordinator/Admin-only. The web AssessmentForm never hit
    this restriction because its category dropdown is a plain Django
    ModelForm queryset resolved server-side, not a call to this API."""
    return Response(AssessmentCategorySerializer(AssessmentCategory.objects.all(), many=True).data)


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
def assessment_list_api(request, offering_id):
    offering = _get_own_offering(request, offering_id)

    if request.method == 'POST':
        form = AssessmentForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        assessment = form.save(commit=False)
        assessment.course_offering = offering
        assessment.created_by = request.user
        assessment.save()
        return Response(AssessmentSerializer(assessment).data, status=status.HTTP_201_CREATED)

    assessments = offering.assessments.select_related('category')
    return Response(AssessmentSerializer(assessments, many=True).data)


@api_view(['GET', 'POST'])
@permission_classes([HasRole.for_roles(*TEACHER_ROLES)])
def enter_marks_api(request, assessment_id):
    profile = resolve_profile(request.user)
    assessment = get_object_or_404(Assessment, pk=assessment_id, course_offering__teacher=profile)

    enrollments = Enrollment.objects.filter(
        course_offering=assessment.course_offering, status=Enrollment.Status.ENROLLED
    ).select_related('student__user')

    if request.method == 'POST':
        raw_value_by_student_id = {
            int(sid): value for sid, value in (request.data or {}).get('marks', {}).items()
        }
        errors = enter_marks_bulk(assessment, raw_value_by_student_id, graded_by=request.user)
        if errors:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Marks saved.'})

    existing = {m.student_id: m.obtained_marks for m in assessment.marks.all()}
    rows = [
        {
            'student_id': e.student.pk, 'roll_number': e.student.roll_number,
            'name': e.student.user.get_full_name(), 'obtained_marks': existing.get(e.student.pk),
        }
        for e in enrollments
    ]
    return Response({'assessment': AssessmentSerializer(assessment).data, 'rows': rows})


@api_view(['GET'])
@permission_classes([HasRole.for_roles(Roles.STUDENT)])
def student_overview_api(request):
    profile = resolve_profile(request.user)
    results = get_student_course_overview(profile)
    # The student's own semester, not "whichever semester happens to be
    # marked current" - see apps/assessments/views.py::student_overview for
    # why semester__is_current isn't specific enough now that a program can
    # have several concurrently-current semesters.
    current_semester_gpa = SemesterGPA.objects.filter(
        student=profile, semester=profile.current_semester
    ).select_related('semester').first()
    cgpa = get_cgpa(profile)
    return Response({
        'results': [
            {
                'course_offering_id': r['course_offering'].pk,
                'course': str(r['course_offering'].course),
                'semester': str(r['course_offering'].semester),
                'total_obtained': r['total_obtained'], 'total_possible': r['total_possible'],
                'percentage': r['percentage'], 'grade_letter': r['grade_letter'],
            }
            for r in results
        ],
        'current_semester_gpa': current_semester_gpa.gpa if current_semester_gpa else None,
        'cgpa': cgpa,
    })


@api_view(['GET'])
@permission_classes([HasRole.for_roles(Roles.STUDENT)])
def student_course_detail_api(request, offering_id):
    profile = resolve_profile(request.user)
    offering = get_object_or_404(
        CourseOffering, pk=offering_id, enrollments__student=profile,
        enrollments__status=Enrollment.Status.ENROLLED,
    )
    result = CourseResult.objects.filter(student=profile, course_offering=offering).first()
    marks = profile.marks.filter(assessment__course_offering=offering).select_related('assessment__category')
    return Response({
        'course': str(offering.course),
        'total_obtained': result.total_obtained if result else None,
        'total_possible': result.total_possible if result else None,
        'percentage': result.percentage if result else None,
        'grade_letter': result.grade_letter if result else None,
        'marks': [
            {
                'assessment_id': m.assessment_id, 'title': m.assessment.title,
                'category': m.assessment.category.name, 'obtained_marks': m.obtained_marks,
                'total_marks': m.assessment.total_marks,
            }
            for m in marks
        ],
    })
