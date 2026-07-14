from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from apps.academics.models import CourseOffering, Semester
from apps.accounts.models import Roles
from apps.common.exports import export_excel, export_pdf
from apps.common.middleware import get_profile
from apps.common.permissions import role_required

from .services import get_academic_report, get_attendance_report, get_merit_list

STAFF_ROLES = (Roles.COORDINATOR, Roles.ADMIN, Roles.TEACHER, Roles.HOD)

ATTENDANCE_HEADERS = ['Roll No.', 'Student', 'Delivered', 'Attended', 'Absent', 'Percentage']
ACADEMIC_HEADERS = ['Roll No.', 'Student', 'Obtained', 'Possible', 'Percentage', 'Grade']
MERIT_HEADERS = ['Rank', 'Roll No.', 'Student', 'GPA', 'Credit Hours']


def _attendance_export_rows(rows):
    return [
        [
            r['student'].roll_number,
            r['student'].user.get_full_name(),
            r['delivered'],
            r['attended'],
            r['absent'],
            r['percentage'] if r['percentage'] is not None else '-',
        ]
        for r in rows
    ]


def _academic_export_rows(rows):
    return [
        [
            r['student'].roll_number,
            r['student'].user.get_full_name(),
            r['total_obtained'],
            r['total_possible'],
            r['percentage'] if r['percentage'] is not None else '-',
            r['grade_letter'] or '-',
        ]
        for r in rows
    ]


def _merit_export_rows(rows):
    return [
        [rank, r.student.roll_number, r.student.user.get_full_name(), r.gpa, r.total_credit_hours]
        for rank, r in enumerate(rows, start=1)
    ]


def _scoped_offerings(request):
    """Coordinator/Admin can report on any active offering; Teacher/HOD only their own."""
    if request.role in (Roles.TEACHER, Roles.HOD):
        profile = get_profile(request)
        return CourseOffering.objects.filter(teacher=profile, is_active=True).select_related(
            'course', 'semester'
        )
    return CourseOffering.objects.filter(is_active=True).select_related('course', 'semester')


@role_required(*STAFF_ROLES)
def reports_home(request):
    return render(request, 'reports/home.html', {})


@role_required(*STAFF_ROLES)
def attendance_report(request):
    offerings = _scoped_offerings(request)
    offering = None
    rows = []
    export_urls = None

    offering_id = request.GET.get('course_offering')
    if offering_id:
        offering = get_object_or_404(offerings, pk=offering_id)
        rows = get_attendance_report(offering)
        export_urls = {
            'excel': f"{reverse('reports:attendance-export-excel')}?course_offering={offering.pk}",
            'pdf': f"{reverse('reports:attendance-export-pdf')}?course_offering={offering.pk}",
        }

    return render(
        request,
        'reports/attendance_report.html',
        {'offerings': offerings, 'offering': offering, 'rows': rows, 'export_urls': export_urls},
    )


@role_required(*STAFF_ROLES)
def attendance_report_excel(request):
    offering = get_object_or_404(_scoped_offerings(request), pk=request.GET.get('course_offering'))
    rows = get_attendance_report(offering)
    return export_excel(
        f'attendance_{offering.course.code}_{offering.semester}', ATTENDANCE_HEADERS, _attendance_export_rows(rows)
    )


@role_required(*STAFF_ROLES)
def attendance_report_pdf(request):
    offering = get_object_or_404(_scoped_offerings(request), pk=request.GET.get('course_offering'))
    rows = get_attendance_report(offering)
    return export_pdf(
        f'attendance_{offering.course.code}_{offering.semester}',
        'Attendance Report',
        ATTENDANCE_HEADERS,
        _attendance_export_rows(rows),
        subtitle=str(offering),
    )


@role_required(*STAFF_ROLES)
def academic_report(request):
    offerings = _scoped_offerings(request)
    offering = None
    rows = []
    export_urls = None

    offering_id = request.GET.get('course_offering')
    if offering_id:
        offering = get_object_or_404(offerings, pk=offering_id)
        rows = get_academic_report(offering)
        export_urls = {
            'excel': f"{reverse('reports:academic-export-excel')}?course_offering={offering.pk}",
            'pdf': f"{reverse('reports:academic-export-pdf')}?course_offering={offering.pk}",
        }

    return render(
        request,
        'reports/academic_report.html',
        {'offerings': offerings, 'offering': offering, 'rows': rows, 'export_urls': export_urls},
    )


@role_required(*STAFF_ROLES)
def academic_report_excel(request):
    offering = get_object_or_404(_scoped_offerings(request), pk=request.GET.get('course_offering'))
    rows = get_academic_report(offering)
    return export_excel(
        f'academic_{offering.course.code}_{offering.semester}', ACADEMIC_HEADERS, _academic_export_rows(rows)
    )


@role_required(*STAFF_ROLES)
def academic_report_pdf(request):
    offering = get_object_or_404(_scoped_offerings(request), pk=request.GET.get('course_offering'))
    rows = get_academic_report(offering)
    return export_pdf(
        f'academic_{offering.course.code}_{offering.semester}',
        'Academic Performance Report',
        ACADEMIC_HEADERS,
        _academic_export_rows(rows),
        subtitle=str(offering),
    )


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def merit_list(request):
    semesters = Semester.objects.select_related('program').order_by('-is_current', 'program__name', '-number')
    semester = None
    rows = []
    export_urls = None

    semester_id = request.GET.get('semester') or (
        semesters.filter(is_current=True).first().pk if semesters.filter(is_current=True).exists() else None
    )
    if semester_id:
        semester = get_object_or_404(Semester, pk=semester_id)
        rows = get_merit_list(semester)
        export_urls = {
            'excel': f"{reverse('reports:merit-export-excel')}?semester={semester.pk}",
            'pdf': f"{reverse('reports:merit-export-pdf')}?semester={semester.pk}",
        }

    return render(
        request,
        'reports/merit_list.html',
        {'semesters': semesters, 'semester': semester, 'rows': rows, 'export_urls': export_urls},
    )


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def merit_list_excel(request):
    semester = get_object_or_404(Semester, pk=request.GET.get('semester'))
    rows = get_merit_list(semester)
    return export_excel(f'merit_list_{semester}', MERIT_HEADERS, _merit_export_rows(rows))


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def merit_list_pdf(request):
    semester = get_object_or_404(Semester, pk=request.GET.get('semester'))
    rows = get_merit_list(semester)
    return export_pdf(f'merit_list_{semester}', 'Semester Merit List', MERIT_HEADERS, _merit_export_rows(rows), subtitle=str(semester))
