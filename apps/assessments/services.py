from decimal import Decimal

from apps.academics.models import Enrollment

from .models import CourseResult, Mark, SemesterGPA

# HEC-style grading scale: (minimum percentage, letter grade, grade point).
GRADE_SCALE = [
    (Decimal('85'), 'A', Decimal('4.00')),
    (Decimal('80'), 'A-', Decimal('3.70')),
    (Decimal('75'), 'B+', Decimal('3.30')),
    (Decimal('71'), 'B', Decimal('3.00')),
    (Decimal('68'), 'B-', Decimal('2.70')),
    (Decimal('64'), 'C+', Decimal('2.30')),
    (Decimal('61'), 'C', Decimal('2.00')),
    (Decimal('58'), 'C-', Decimal('1.70')),
    (Decimal('54'), 'D+', Decimal('1.30')),
    (Decimal('50'), 'D', Decimal('1.00')),
    (Decimal('0'), 'F', Decimal('0.00')),
]


def grade_for_percentage(percentage):
    for minimum, letter, point in GRADE_SCALE:
        if percentage >= minimum:
            return letter, point
    return 'F', Decimal('0.00')


def recalculate_course_result(student, course_offering):
    marks = Mark.objects.filter(student=student, assessment__course_offering=course_offering).select_related(
        'assessment'
    )

    total_obtained = sum((m.obtained_marks for m in marks), Decimal('0'))
    total_possible = sum((m.assessment.total_marks for m in marks), Decimal('0'))

    graded_weight = sum((m.assessment.weight_percent for m in marks), Decimal('0'))
    if graded_weight > 0:
        weighted_score = sum(
            ((m.obtained_marks / m.assessment.total_marks) * m.assessment.weight_percent for m in marks),
            Decimal('0'),
        )
        percentage = (weighted_score / graded_weight) * 100
        percentage = percentage.quantize(Decimal('0.01'))
        grade_letter, grade_point = grade_for_percentage(percentage)
    else:
        percentage = None
        grade_letter = ''
        grade_point = None

    result, _ = CourseResult.objects.update_or_create(
        student=student,
        course_offering=course_offering,
        defaults={
            'total_obtained': total_obtained,
            'total_possible': total_possible,
            'percentage': percentage,
            'grade_letter': grade_letter,
            'grade_point': grade_point,
        },
    )

    recalculate_semester_gpa(student, course_offering.semester)
    return result


def recalculate_semester_gpa(student, semester):
    results = CourseResult.objects.filter(
        student=student, course_offering__semester=semester, grade_point__isnull=False
    ).select_related('course_offering__course')

    total_credit_hours = 0
    quality_points = Decimal('0')
    for result in results:
        credit_hours = result.course_offering.course.credit_hours
        total_credit_hours += credit_hours
        quality_points += result.grade_point * credit_hours

    gpa = (quality_points / total_credit_hours).quantize(Decimal('0.01')) if total_credit_hours else None

    SemesterGPA.objects.update_or_create(
        student=student,
        semester=semester,
        defaults={'gpa': gpa, 'total_credit_hours': total_credit_hours},
    )


def get_student_course_overview(student):
    """One row per enrolled course, even if nothing has been graded yet."""
    enrollments = student.enrollments.filter(status=Enrollment.Status.ENROLLED).select_related(
        'course_offering__course', 'course_offering__semester'
    )
    results_by_offering = {
        r.course_offering_id: r
        for r in CourseResult.objects.filter(student=student).select_related('course_offering')
    }

    rows = []
    for enrollment in enrollments:
        offering = enrollment.course_offering
        result = results_by_offering.get(offering.id)
        rows.append(
            {
                'course_offering': offering,
                'total_obtained': result.total_obtained if result else Decimal('0'),
                'total_possible': result.total_possible if result else Decimal('0'),
                'percentage': result.percentage if result else None,
                'grade_letter': result.grade_letter if result else '',
            }
        )
    return rows


def get_cgpa(student):
    gpas = SemesterGPA.objects.filter(student=student, gpa__isnull=False)
    total_credit_hours = sum((g.total_credit_hours for g in gpas), 0)
    if not total_credit_hours:
        return None
    quality_points = sum((g.gpa * g.total_credit_hours for g in gpas), Decimal('0'))
    return (quality_points / total_credit_hours).quantize(Decimal('0.01'))
