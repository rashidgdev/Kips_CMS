from decimal import Decimal

from apps.academics.models import Enrollment
from apps.assessments.models import AssessmentCategory, CourseResult, Mark, SemesterGPA
from apps.attendance.services import get_student_course_stats


def get_teacher_assignments_overview():
    """One row per teacher - how many subjects they teach, and which
    course/semester/section each one is. Distinct from
    apps.daybook.services.get_all_teachers_workload (payroll: lecture
    counts/pay, no course names) and CourseOfferingListView (a flat,
    ungrouped list of every offering, not grouped by teacher)."""
    from django.db.models import Prefetch

    from apps.academics.models import CourseOffering
    from apps.accounts.models import TeacherProfile

    # A plain 'course_offerings__course' prefetch would cache ALL of a
    # teacher's offerings; calling .filter(is_active=True) on the related
    # manager in the loop below would then bypass that cache and re-query
    # per teacher (N+1). A Prefetch with its own filtered/ordered queryset
    # avoids that - .all() in the loop reads straight from the prefetch cache.
    active_offerings = Prefetch(
        'course_offerings',
        queryset=CourseOffering.objects.filter(is_active=True)
        .select_related('course', 'semester')
        .order_by('-semester__is_current', 'semester', 'course'),
    )
    teachers = (
        TeacherProfile.objects.select_related('user', 'department')
        .prefetch_related(active_offerings)
        .order_by('employee_id')
    )

    rows = []
    for teacher in teachers:
        offerings = list(teacher.course_offerings.all())
        rows.append({'teacher': teacher, 'offering_count': len(offerings), 'offerings': offerings})
    return rows


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


def get_student_progress_report(student, semester):
    """Combined progress report for one student in one semester: attendance,
    a per-assessment-category breakdown (quiz/assignment/presentation/mid/
    final), per-course results, and semester GPA - the data behind the
    downloadable "result card"."""
    enrollments = list(
        Enrollment.objects.filter(
            student=student, course_offering__semester=semester, status=Enrollment.Status.ENROLLED
        ).select_related('course_offering__course')
    )
    results_by_offering = {
        r.course_offering_id: r
        for r in CourseResult.objects.filter(student=student, course_offering__semester=semester)
    }

    course_rows = []
    attendance_delivered_total = 0
    attendance_attended_total = 0
    category_totals = {}

    for enrollment in enrollments:
        offering = enrollment.course_offering
        attendance = get_student_course_stats(student, offering)
        attendance_delivered_total += attendance['delivered']
        attendance_attended_total += attendance['attended']

        course_rows.append(
            {
                'offering': offering,
                'attendance': attendance,
                'result': results_by_offering.get(offering.id),
            }
        )

        marks = Mark.objects.filter(
            student=student, assessment__course_offering=offering
        ).select_related('assessment__category')
        for mark in marks:
            category_name = mark.assessment.category.name
            totals = category_totals.setdefault(
                category_name, {'obtained': Decimal('0'), 'possible': Decimal('0')}
            )
            totals['obtained'] += mark.obtained_marks
            totals['possible'] += mark.assessment.total_marks

    category_breakdown = []
    for category in AssessmentCategory.objects.order_by('name'):
        totals = category_totals.get(category.name)
        if totals and totals['possible'] > 0:
            percentage = round((totals['obtained'] / totals['possible']) * 100, 1)
        else:
            percentage = None
        category_breakdown.append(
            {
                'name': category.name,
                'obtained': totals['obtained'] if totals else Decimal('0'),
                'possible': totals['possible'] if totals else Decimal('0'),
                'percentage': percentage,
            }
        )

    attendance_percentage = (
        round((attendance_attended_total / attendance_delivered_total) * 100, 1)
        if attendance_delivered_total
        else None
    )

    return {
        'student': student,
        'semester': semester,
        'course_rows': course_rows,
        'category_breakdown': category_breakdown,
        'attendance_overall': {
            'delivered': attendance_delivered_total,
            'attended': attendance_attended_total,
            'percentage': attendance_percentage,
        },
        'semester_gpa': SemesterGPA.objects.filter(student=student, semester=semester).first(),
    }
