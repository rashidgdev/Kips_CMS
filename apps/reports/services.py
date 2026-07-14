from decimal import Decimal

from apps.academics.models import Enrollment
from apps.assessments.models import CourseResult, SemesterGPA
from apps.attendance.services import get_student_course_stats


def get_attendance_report(course_offering):
    enrollments = Enrollment.objects.filter(
        course_offering=course_offering, status=Enrollment.Status.ENROLLED
    ).select_related('student__user')

    rows = []
    for enrollment in enrollments:
        stats = get_student_course_stats(enrollment.student, course_offering)
        rows.append({'student': enrollment.student, **stats})
    return rows


def get_academic_report(course_offering):
    enrollments = Enrollment.objects.filter(
        course_offering=course_offering, status=Enrollment.Status.ENROLLED
    ).select_related('student__user')
    results_by_student = {
        r.student_id: r for r in CourseResult.objects.filter(course_offering=course_offering)
    }

    rows = []
    for enrollment in enrollments:
        result = results_by_student.get(enrollment.student_id)
        rows.append(
            {
                'student': enrollment.student,
                'total_obtained': result.total_obtained if result else Decimal('0'),
                'total_possible': result.total_possible if result else Decimal('0'),
                'percentage': result.percentage if result else None,
                'grade_letter': result.grade_letter if result else '',
            }
        )
    return rows


def get_merit_list(semester):
    return list(
        SemesterGPA.objects.filter(semester=semester, gpa__isnull=False)
        .select_related('student__user')
        .order_by('-gpa')
    )
