from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.models import Roles
from apps.common.middleware import get_profile
from apps.common.permissions import role_required

from . import services as dashboard_services

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
    profile = get_profile(request)
    data = dashboard_services.get_student_dashboard_data(profile)
    return render(request, 'dashboard/student.html', {'profile': profile, **data})


@role_required(Roles.TEACHER)
def teacher_dashboard(request):
    profile = get_profile(request)
    data = dashboard_services.get_teacher_dashboard_data(profile)
    return render(request, 'dashboard/teacher.html', {'profile': profile, **data})


@role_required(Roles.HOD)
def hod_dashboard(request):
    profile = get_profile(request)
    data = dashboard_services.get_hod_dashboard_data(profile)
    return render(request, 'dashboard/hod.html', {'profile': profile, **data})


@role_required(Roles.COORDINATOR)
def coordinator_dashboard(request):
    return render(request, 'dashboard/coordinator.html', dashboard_services.get_coordinator_dashboard_data())


@role_required(Roles.ACCOUNTANT)
def accountant_dashboard(request):
    return render(request, 'dashboard/accountant.html', dashboard_services.get_accountant_dashboard_data())


@role_required(Roles.ADMIN)
def admin_dashboard(request):
    return render(request, 'dashboard/admin.html', dashboard_services.get_admin_dashboard_data())


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
        'teacher_assignments_url': reverse('reports:teacher-assignments'),
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
