from apps.accounts.models import TeacherProfile
from apps.attendance.models import LectureSession

from .models import DayBookEntry


def get_teacher_workload(teacher, year, month):
    sessions = LectureSession.objects.filter(
        course_offering__teacher=teacher, date__year=year, date__month=month
    )
    total_lectures = sessions.count()
    verified_lectures = DayBookEntry.objects.filter(
        session__in=sessions, verified_by__isnull=False
    ).count()
    rate = teacher.per_lecture_rate
    total_amount = verified_lectures * rate

    return {
        'teacher': teacher,
        'total_lectures': total_lectures,
        'verified_lectures': verified_lectures,
        'unverified_lectures': total_lectures - verified_lectures,
        'per_lecture_rate': rate,
        'total_amount': total_amount,
    }


def get_all_teachers_workload(year, month):
    teachers = TeacherProfile.objects.select_related('user', 'department').order_by('employee_id')
    return [get_teacher_workload(teacher, year, month) for teacher in teachers]
