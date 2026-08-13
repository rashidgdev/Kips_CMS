from django.conf import settings

from .models import AttendanceRecord

ATTENDED_STATUSES = (AttendanceRecord.Status.PRESENT, AttendanceRecord.Status.LATE)


def mark_attendance_bulk(session, status_by_student_id, marked_by):
    """Upserts one AttendanceRecord per (session, student) pair - shared by
    the Django view (views.py::mark_attendance) and the REST API, so the
    same "unknown status silently falls back to Present" rule applies
    identically everywhere. `status_by_student_id` is a
    {student_pk: status_string} mapping; only students already ENROLLED in
    the session's course offering are ever written (extra/unknown student
    ids in the mapping are ignored)."""
    from apps.academics.models import Enrollment

    enrollments = Enrollment.objects.filter(
        course_offering=session.course_offering, status=Enrollment.Status.ENROLLED
    ).select_related('student')

    saved = []
    for enrollment in enrollments:
        student = enrollment.student
        status = status_by_student_id.get(student.pk, AttendanceRecord.Status.PRESENT)
        if status not in AttendanceRecord.Status.values:
            status = AttendanceRecord.Status.PRESENT
        record, _ = AttendanceRecord.objects.update_or_create(
            session=session, student=student, defaults={'status': status, 'marked_by': marked_by},
        )
        saved.append(record)
    return saved


def get_student_course_stats(student, course_offering):
    """Compute delivered/attended/absent lecture counts and % for one student+course."""
    records = AttendanceRecord.objects.filter(session__course_offering=course_offering, student=student)
    delivered = records.count()
    attended = records.filter(status__in=ATTENDED_STATUSES).count()
    absent = delivered - attended
    percentage = round((attended / delivered) * 100, 1) if delivered else None
    threshold = settings.ATTENDANCE_SHORTAGE_THRESHOLD
    return {
        'course_offering': course_offering,
        'delivered': delivered,
        'attended': attended,
        'absent': absent,
        'percentage': percentage,
        'threshold': threshold,
        'is_shortage': percentage is not None and percentage < threshold,
    }


def get_student_overview(student):
    course_offerings = [
        e.course_offering for e in student.enrollments.select_related('course_offering__course').all()
    ]
    return [get_student_course_stats(student, offering) for offering in course_offerings]
