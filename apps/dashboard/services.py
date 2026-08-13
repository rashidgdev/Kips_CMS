"""
Business logic shared between the Django dashboard views (views.py) and
their REST API equivalent (api_views.py). Was previously inline in each
Django view - extracted so neither implementation duplicates the other.
"""
import datetime


def get_student_dashboard_data(profile):
    from apps.assessments.models import SemesterGPA
    from apps.assessments.services import get_cgpa
    from apps.attendance.services import get_student_overview as get_attendance_overview

    enrollments = list(
        profile.enrollments.select_related('course_offering__course', 'course_offering__teacher__user')
    ) if profile else []

    cgpa = current_gpa = overall_attendance = None
    if profile:
        cgpa = get_cgpa(profile)
        # The student's own semester - a program can have several concurrent
        # current semesters (different cohorts), so semester__is_current
        # isn't specific enough to identify this particular student's one.
        current_gpa = SemesterGPA.objects.filter(student=profile, semester=profile.current_semester).first()
        percentages = [s['percentage'] for s in get_attendance_overview(profile) if s['percentage'] is not None]
        if percentages:
            overall_attendance = round(sum(percentages) / len(percentages), 1)

    return {
        'enrollments': enrollments, 'cgpa': cgpa, 'current_gpa': current_gpa,
        'overall_attendance': overall_attendance,
    }


def get_teacher_dashboard_data(profile):
    from apps.timetable.models import TimetableEntry

    offerings = list(profile.course_offerings.select_related('course', 'semester')) if profile else []
    todays_classes = list(
        TimetableEntry.objects.filter(
            course_offering__teacher=profile, time_slot__day_of_week=datetime.date.today().isoweekday()
        ).select_related('time_slot', 'room', 'course_offering__course').order_by('time_slot__start_time')
    ) if profile else []
    return {'offerings': offerings, 'todays_classes': todays_classes}


def get_hod_dashboard_data(profile):
    department = getattr(profile, 'department', None)
    offerings = list(profile.course_offerings.select_related('course', 'semester')) if profile else []
    return {'department': department, 'offerings': offerings}


def get_coordinator_dashboard_data():
    from apps.academics.models import CourseOffering, Program

    return {
        'program_count': Program.objects.filter(is_active=True).count(),
        'offering_count': CourseOffering.objects.filter(is_active=True).count(),
    }


def get_accountant_dashboard_data():
    from apps.finance.services import get_all_students_fee_summary

    summary = get_all_students_fee_summary()
    return {
        'student_count': len(summary),
        'total_due': sum((row['total_due'] for row in summary), 0),
        'total_paid': sum((row['total_paid'] for row in summary), 0),
        'total_outstanding': sum((row['total_outstanding'] for row in summary), 0),
    }


def get_admin_dashboard_data():
    from apps.accounts.models import Roles, User

    return {'user_counts': {role.label: User.objects.filter(role=role).count() for role in Roles}}
