from django.conf import settings

from .models import AttendanceRecord

ATTENDED_STATUSES = (AttendanceRecord.Status.PRESENT, AttendanceRecord.Status.LATE)


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
