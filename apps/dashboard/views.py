from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.models import Roles
from apps.common.middleware import get_profile
from apps.common.permissions import role_required

ROLE_DASHBOARD_URL_NAME = {
    Roles.STUDENT: 'dashboard:student',
    Roles.TEACHER: 'dashboard:teacher',
    Roles.HOD: 'dashboard:hod',
    Roles.COORDINATOR: 'dashboard:coordinator',
    Roles.ACCOUNTANT: 'dashboard:accountant',
    Roles.ADMIN: 'dashboard:admin',
}


@login_required
def dashboard_redirect(request):
    url_name = ROLE_DASHBOARD_URL_NAME.get(request.user.role, 'accounts:login')
    return redirect(url_name)


@role_required(Roles.STUDENT)
def student_dashboard(request):
    from apps.assessments.models import SemesterGPA
    from apps.assessments.services import get_cgpa
    from apps.attendance.services import get_student_overview as get_attendance_overview

    profile = get_profile(request)
    enrollments = profile.enrollments.select_related(
        'course_offering__course', 'course_offering__teacher__user'
    ) if profile else []

    cgpa = current_gpa = overall_attendance = None
    if profile:
        cgpa = get_cgpa(profile)
        current_gpa = SemesterGPA.objects.filter(student=profile, semester__is_current=True).first()
        percentages = [s['percentage'] for s in get_attendance_overview(profile) if s['percentage'] is not None]
        if percentages:
            overall_attendance = round(sum(percentages) / len(percentages), 1)

    return render(
        request,
        'dashboard/student.html',
        {
            'profile': profile,
            'enrollments': enrollments,
            'cgpa': cgpa,
            'current_gpa': current_gpa,
            'overall_attendance': overall_attendance,
        },
    )


@role_required(Roles.TEACHER)
def teacher_dashboard(request):
    import datetime

    from apps.timetable.models import TimetableEntry

    profile = get_profile(request)
    offerings = profile.course_offerings.select_related('course', 'semester') if profile else []
    todays_classes = TimetableEntry.objects.filter(
        course_offering__teacher=profile, time_slot__day_of_week=datetime.date.today().isoweekday()
    ).select_related('time_slot', 'room', 'course_offering__course').order_by('time_slot__start_time') if profile else []

    return render(
        request,
        'dashboard/teacher.html',
        {'profile': profile, 'offerings': offerings, 'todays_classes': todays_classes},
    )


@role_required(Roles.HOD)
def hod_dashboard(request):
    profile = get_profile(request)
    department = getattr(profile, 'department', None)
    offerings = profile.course_offerings.select_related('course', 'semester') if profile else []
    return render(
        request, 'dashboard/hod.html', {'profile': profile, 'department': department, 'offerings': offerings}
    )


@role_required(Roles.COORDINATOR)
def coordinator_dashboard(request):
    from apps.academics.models import CourseOffering, Program

    context = {
        'program_count': Program.objects.filter(is_active=True).count(),
        'offering_count': CourseOffering.objects.filter(is_active=True).count(),
    }
    return render(request, 'dashboard/coordinator.html', context)


@role_required(Roles.ACCOUNTANT)
def accountant_dashboard(request):
    from apps.finance.services import get_all_students_fee_summary

    summary = get_all_students_fee_summary()
    context = {
        'student_count': len(summary),
        'total_due': sum((row['total_due'] for row in summary), 0),
        'total_paid': sum((row['total_paid'] for row in summary), 0),
        'total_outstanding': sum((row['total_outstanding'] for row in summary), 0),
    }
    return render(request, 'dashboard/accountant.html', context)


@role_required(Roles.ADMIN)
def admin_dashboard(request):
    from apps.accounts.models import User

    context = {'user_counts': {role.label: User.objects.filter(role=role).count() for role in Roles}}
    return render(request, 'dashboard/admin.html', context)


@role_required(Roles.COORDINATOR, Roles.ACCOUNTANT, Roles.ADMIN)
def admin_portal(request):
    from django.urls import reverse

    context = {
        'people_url': reverse('accounts:people'),
        'departments_url': reverse('accounts:departments'),
        'programs_url': reverse('academics:programs'),
        'semesters_url': reverse('academics:semesters'),
        'courses_url': reverse('academics:courses'),
        'offerings_url': reverse('academics:offerings'),
        'enrollments_url': reverse('academics:enrollments'),
        'enroll_by_offering_url': reverse('academics:enroll-by-offering'),
        'enroll_by_student_url': reverse('academics:enroll-by-student'),
        'rooms_url': reverse('timetable:rooms'),
        'timeslots_url': reverse('timetable:timeslots'),
        'assessment_categories_url': reverse('assessments:categories'),
        'fee_categories_url': reverse('finance:categories'),
        'fee_structures_url': reverse('finance:structures'),
    }
    return render(request, 'dashboard/admin_portal.html', context)
