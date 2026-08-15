from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.academics.models import CourseOffering, Enrollment
from apps.accounts.models import Roles
from apps.common.middleware import get_profile
from apps.common.pagination import paginate_queryset
from apps.common.permissions import role_required

from .forms import LectureSessionForm
from .models import AttendanceRecord, LectureSession
from .services import get_student_course_stats, get_student_overview, mark_attendance_bulk


@role_required(Roles.TEACHER, Roles.HOD)
def offering_list(request):
    profile = get_profile(request)
    offerings = paginate_queryset(
        request, profile.course_offerings.select_related('course', 'semester').filter(is_active=True)
    )
    return render(request, 'attendance/offering_list.html', {'offerings': offerings, 'is_paginated': offerings.has_other_pages()})


def _get_own_offering(request, offering_id):
    profile = get_profile(request)
    return get_object_or_404(CourseOffering, pk=offering_id, teacher=profile)


@role_required(Roles.TEACHER, Roles.HOD)
def session_list(request, offering_id):
    offering = _get_own_offering(request, offering_id)
    sessions = paginate_queryset(request, offering.sessions.all())
    return render(
        request, 'attendance/session_list.html',
        {'offering': offering, 'sessions': sessions, 'is_paginated': sessions.has_other_pages()},
    )


@role_required(Roles.TEACHER, Roles.HOD)
def session_create(request, offering_id):
    offering = _get_own_offering(request, offering_id)

    if request.method == 'POST':
        form = LectureSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.course_offering = offering
            session.created_by = request.user
            session.save()
            return redirect('attendance:mark', session_id=session.pk)
    else:
        form = LectureSessionForm()

    return render(request, 'attendance/session_form.html', {'offering': offering, 'form': form})


@role_required(Roles.TEACHER, Roles.HOD)
def mark_attendance(request, session_id):
    profile = get_profile(request)
    session = get_object_or_404(LectureSession, pk=session_id, course_offering__teacher=profile)

    enrollments = Enrollment.objects.filter(
        course_offering=session.course_offering, status=Enrollment.Status.ENROLLED
    ).select_related('student__user')

    existing = {r.student_id: r.status for r in session.records.all()}

    if request.method == 'POST':
        status_by_student_id = {
            enrollment.student.pk: request.POST.get(f'status_{enrollment.student.pk}', AttendanceRecord.Status.PRESENT)
            for enrollment in enrollments
        }
        mark_attendance_bulk(session, status_by_student_id, marked_by=request.user)
        messages.success(request, 'Attendance saved.')
        return redirect('attendance:sessions', offering_id=session.course_offering_id)

    rows = [
        {'student': e.student, 'status': existing.get(e.student_id, AttendanceRecord.Status.PRESENT)}
        for e in enrollments
    ]
    return render(
        request,
        'attendance/mark_attendance.html',
        {'session': session, 'rows': rows, 'status_choices': AttendanceRecord.Status.choices},
    )


@role_required(Roles.STUDENT)
def student_overview(request):
    profile = get_profile(request)
    stats = get_student_overview(profile)
    return render(request, 'attendance/student_overview.html', {'stats': stats})


@role_required(Roles.STUDENT)
def student_course_detail(request, offering_id):
    profile = get_profile(request)
    offering = get_object_or_404(
        CourseOffering, pk=offering_id, enrollments__student=profile,
        enrollments__status=Enrollment.Status.ENROLLED,
    )
    stat = get_student_course_stats(profile, offering)
    records = paginate_queryset(
        request,
        AttendanceRecord.objects.filter(
            session__course_offering=offering, student=profile
        ).select_related('session'),
    )
    return render(
        request,
        'attendance/student_course_detail.html',
        {'offering': offering, 'stat': stat, 'records': records, 'is_paginated': records.has_other_pages()},
    )
