"""
Business logic shared between the Django dashboard views (views.py) and
their REST API equivalent (api_views.py). Was previously inline in each
Django view - extracted so neither implementation duplicates the other.
"""
import datetime


def get_student_dashboard_data(profile):
    from apps.academics.models import Enrollment
    from apps.assessments.models import SemesterGPA
    from apps.assessments.services import get_cgpa, get_student_course_overview
    from apps.attendance.services import get_student_overview as get_attendance_overview
    from apps.finance.services import get_student_fee_overview
    from apps.timetable.models import TimetableEntry

    enrollments = list(
        profile.enrollments.select_related('course_offering__course', 'course_offering__teacher__user')
    ) if profile else []

    cgpa = current_gpa = overall_attendance = fee_overview = None
    attendance_rows = []
    marks_rows = []
    todays_classes = []
    if profile:
        cgpa = get_cgpa(profile)
        # The student's own semester - a program can have several concurrent
        # current semesters (different cohorts), so semester__is_current
        # isn't specific enough to identify this particular student's one.
        current_gpa = SemesterGPA.objects.filter(student=profile, semester=profile.current_semester).first()
        attendance_rows = get_attendance_overview(profile)
        percentages = [s['percentage'] for s in attendance_rows if s['percentage'] is not None]
        if percentages:
            overall_attendance = round(sum(percentages) / len(percentages), 1)
        marks_rows = get_student_course_overview(profile)
        fee_overview = get_student_fee_overview(profile)
        todays_classes = list(
            TimetableEntry.objects.filter(
                course_offering__enrollments__student=profile,
                course_offering__enrollments__status=Enrollment.Status.ENROLLED,
                time_slot__day_of_week=datetime.date.today().isoweekday(),
            )
            .select_related('time_slot', 'room', 'course_offering__course')
            .distinct()
            .order_by('time_slot__start_time')
        )

    # Progress rings display GPA-out-of-4.0 as a 0-100 fill percentage -
    # computed here rather than in the template, since Django's {% widthratio %}
    # tag can't be captured into a variable for re-use inside an {% include %}.
    cgpa_percent = min(int(float(cgpa) / 4 * 100), 100) if cgpa else 0
    current_gpa_percent = (
        min(int(float(current_gpa.gpa) / 4 * 100), 100) if current_gpa and current_gpa.gpa is not None else 0
    )

    return {
        'enrollments': enrollments,
        'cgpa': cgpa,
        'cgpa_percent': cgpa_percent,
        'current_gpa': current_gpa,
        'current_gpa_percent': current_gpa_percent,
        'overall_attendance': overall_attendance,
        'attendance_rows': attendance_rows,
        'marks_rows': marks_rows,
        'fee_overview': fee_overview,
        'todays_classes': todays_classes,
    }


def get_teacher_dashboard_data(profile):
    from apps.academics.models import Enrollment
    from apps.daybook.models import DayBookEntry
    from apps.daybook.services import get_teacher_workload
    from apps.timetable.models import TimetableEntry

    offerings = list(profile.course_offerings.select_related('course', 'semester')) if profile else []
    todays_classes = list(
        TimetableEntry.objects.filter(
            course_offering__teacher=profile, time_slot__day_of_week=datetime.date.today().isoweekday()
        ).select_related('time_slot', 'room', 'course_offering__course').order_by('time_slot__start_time')
    ) if profile else []

    student_count = 0
    workload = None
    unverified_count = 0
    if profile:
        student_count = (
            Enrollment.objects.filter(course_offering__teacher=profile, status=Enrollment.Status.ENROLLED)
            .values('student_id').distinct().count()
        )
        today = datetime.date.today()
        workload = get_teacher_workload(profile, today.year, today.month)
        unverified_count = DayBookEntry.objects.filter(
            session__course_offering__teacher=profile, verified_by__isnull=True
        ).count()

    return {
        'offerings': offerings,
        'todays_classes': todays_classes,
        'student_count': student_count,
        'workload': workload,
        'unverified_count': unverified_count,
    }


def get_hod_dashboard_data(profile):
    from apps.academics.models import CourseOffering
    from apps.accounts.models import TeacherProfile

    department = getattr(profile, 'department', None)
    # An HOD is a TeacherProfile, so their own teaching load/workload/today's
    # classes are identical in shape to a Teacher's - reuse that wholesale
    # instead of recomputing it, then layer department-wide numbers on top.
    data = get_teacher_dashboard_data(profile)
    data['department'] = department
    data['department_teacher_count'] = (
        TeacherProfile.objects.filter(department=department).count() if department else 0
    )
    data['department_offering_count'] = (
        CourseOffering.objects.filter(is_active=True, teacher__department=department).count()
        if department else 0
    )
    return data


def get_coordinator_dashboard_data():
    from apps.academics.models import CourseOffering, Program
    from apps.accounts.models import Roles, User
    from apps.daybook.models import DayBookEntry
    from apps.daybook.services import get_all_teachers_workload
    from apps.finance.services import get_all_students_fee_summary

    today = datetime.date.today()
    fee_summary = get_all_students_fee_summary()
    workload_rows = get_all_teachers_workload(today.year, today.month)

    return {
        'program_count': Program.objects.filter(is_active=True).count(),
        'offering_count': CourseOffering.objects.filter(is_active=True).count(),
        'user_counts': {role.label: User.objects.filter(role=role).count() for role in Roles},
        'total_outstanding': sum((row['total_outstanding'] for row in fee_summary), 0),
        'unverified_count': DayBookEntry.objects.filter(verified_by__isnull=True).count(),
        'workload_total': sum((row['total_amount'] for row in workload_rows), 0),
    }


def get_accountant_dashboard_data():
    from apps.finance.models import Payment, StudentFeeItem
    from apps.finance.services import get_all_students_fee_summary, get_fee_item_balance

    summary = get_all_students_fee_summary()

    overdue_count = sum(
        1
        for item in StudentFeeItem.objects.select_related('student').prefetch_related('payments')
        if get_fee_item_balance(item)['status'] == 'overdue'
    )
    recent_payments = list(
        Payment.objects.select_related('fee_item__student__user', 'fee_item__category')
        .order_by('-payment_date', '-pk')[:8]
    )

    by_program = {}
    for row in summary:
        program = row['student'].program
        key = program.code if program else 'Unassigned'
        bucket = by_program.setdefault(key, {'label': key, 'value': 0})
        bucket['value'] += row['total_outstanding']
    program_breakdown = sorted(by_program.values(), key=lambda b: b['value'], reverse=True)[:6]
    breakdown_total = sum(b['value'] for b in program_breakdown) or 1
    palette = ['bg-blue-500', 'bg-indigo-500', 'bg-emerald-500', 'bg-amber-500', 'bg-rose-500', 'bg-violet-500']
    for index, bucket in enumerate(program_breakdown):
        bucket['percent'] = round(bucket['value'] / breakdown_total * 100, 1)
        bucket['color'] = palette[index % len(palette)]

    return {
        'student_count': len(summary),
        'total_due': sum((row['total_due'] for row in summary), 0),
        'total_paid': sum((row['total_paid'] for row in summary), 0),
        'total_outstanding': sum((row['total_outstanding'] for row in summary), 0),
        'overdue_count': overdue_count,
        'recent_payments': recent_payments,
        'program_breakdown': program_breakdown,
    }


def get_admin_dashboard_data():
    from django.db.models import Count

    from apps.accounts.models import Department, Roles, StudentProfile, User

    coordinator_data = get_coordinator_dashboard_data()
    accountant_data = get_accountant_dashboard_data()

    status_counts = {
        row['status']: row['count']
        for row in StudentProfile.objects.values('status').annotate(count=Count('id'))
    }
    status_labels = dict(StudentProfile.Status.choices)
    status_palette = {
        StudentProfile.Status.ACTIVE: 'bg-emerald-500',
        StudentProfile.Status.GRADUATED: 'bg-blue-500',
        StudentProfile.Status.DROPPED: 'bg-gray-400',
        StudentProfile.Status.SUSPENDED: 'bg-amber-500',
    }
    total_students = sum(status_counts.values()) or 1
    student_status_breakdown = [
        {
            'label': status_labels.get(status, status),
            'value': count,
            'percent': round(count / total_students * 100, 1),
            'color': status_palette.get(status, 'bg-gray-400'),
        }
        for status, count in status_counts.items() if count
    ]

    return {
        'user_counts': {role.label: User.objects.filter(role=role).count() for role in Roles},
        'department_count': Department.objects.count(),
        'student_status_breakdown': student_status_breakdown,
        'coordinator': coordinator_data,
        'accountant': accountant_data,
    }
