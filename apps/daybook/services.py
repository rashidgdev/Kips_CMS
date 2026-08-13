from django.utils import timezone

from apps.accounts.models import TeacherProfile
from apps.attendance.models import LectureSession

from .models import DayBookEntry, MonthlyWorkloadSnapshot


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


def verify_day_book_entry(entry, verified_by, remarks=''):
    """Marks a day book entry (one delivered lecture) as verified by a
    Coordinator/Admin - this is what makes it count toward payroll (see
    get_teacher_workload, which only counts verified_lectures)."""
    entry.verified_by = verified_by
    entry.verified_at = timezone.now()
    entry.remarks = remarks
    entry.save(update_fields=['verified_by', 'verified_at', 'remarks', 'updated_at'])
    return entry


def generate_workload_snapshots(year, month, generated_by):
    """Freezes each teacher's current workload numbers for `year`/`month`
    into an auditable MonthlyWorkloadSnapshot row - re-running for the same
    month updates the existing snapshot rather than duplicating it, so a
    Coordinator can safely regenerate after late verifications come in."""
    rows = get_all_teachers_workload(year, month)
    for row in rows:
        MonthlyWorkloadSnapshot.objects.update_or_create(
            teacher=row['teacher'],
            year=year,
            month=month,
            defaults={
                'total_lectures': row['total_lectures'],
                'verified_lectures': row['verified_lectures'],
                'per_lecture_rate': row['per_lecture_rate'],
                'total_amount': row['total_amount'],
                'generated_by': generated_by,
            },
        )
    return rows
