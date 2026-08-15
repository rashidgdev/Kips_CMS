from .models import Enrollment


def bulk_enroll_by_offering(course_offering, student_ids):
    """Enrolls many students into one course offering at once - shared by the
    Django view (views.py::enroll_by_offering) and the REST API. Students
    already enrolled are silently skipped (not re-created, not an error),
    matching the web view's exact behavior. Stops once the offering's
    max_seats is reached rather than overfilling a section - any requested
    students beyond that are left unenrolled. Returns
    (enrolled_count, skipped_for_capacity_count)."""
    already_enrolled_ids = set(course_offering.enrollments.values_list('student_id', flat=True))
    new_ids = list(set(student_ids) - already_enrolled_ids)

    free_seats = max(course_offering.max_seats - len(already_enrolled_ids), 0)
    to_enroll, skipped = new_ids[:free_seats], new_ids[free_seats:]

    Enrollment.objects.bulk_create(
        [Enrollment(student_id=sid, course_offering=course_offering) for sid in to_enroll]
    )
    return len(to_enroll), len(skipped)


def bulk_enroll_by_student(student, course_offering_ids):
    """Enrolls one student into many course offerings at once - shared by
    the Django view (views.py::enroll_by_student) and the REST API. Course
    offerings the student is already enrolled in are silently skipped,
    matching the web view's exact behavior. Returns the number newly
    enrolled."""
    already_enrolled_ids = set(student.enrollments.values_list('course_offering_id', flat=True))
    new_ids = set(course_offering_ids) - already_enrolled_ids
    Enrollment.objects.bulk_create(
        [Enrollment(student=student, course_offering_id=oid) for oid in new_ids]
    )
    return len(new_ids)
