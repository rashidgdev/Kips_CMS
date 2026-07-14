"""
Exposes role/navigation context to every template so `base.html` renders
per-role navigation from one config dict instead of scattered
`{% if role == "..." %}` chains.
"""
from django.urls import reverse

NAV_CONFIG = {
    'student': [
        {'label': 'Dashboard', 'url_name': 'dashboard:student', 'icon': 'dashboard'},
        {'label': 'Attendance', 'url_name': 'attendance:student-overview', 'icon': 'clipboard-list'},
        {'label': 'Grades', 'url_name': 'assessments:student-overview', 'icon': 'academic-cap'},
        {'label': 'Timetable', 'url_name': 'timetable:student-mine', 'icon': 'calendar'},
        {'label': 'Fees', 'url_name': 'finance:student-overview', 'icon': 'currency'},
    ],
    'teacher': [
        {'label': 'Dashboard', 'url_name': 'dashboard:teacher', 'icon': 'dashboard'},
        {'label': 'Attendance', 'url_name': 'attendance:offerings', 'icon': 'clipboard-list'},
        {'label': 'Day Book', 'url_name': 'daybook:mine', 'icon': 'book-open'},
        {'label': 'Assessments', 'url_name': 'assessments:offerings', 'icon': 'document-chart'},
        {'label': 'Timetable', 'url_name': 'timetable:teacher-mine', 'icon': 'calendar'},
        {'label': 'Reports', 'url_name': 'reports:home', 'icon': 'chart-bar'},
    ],
    'hod': [
        {'label': 'Dashboard', 'url_name': 'dashboard:hod', 'icon': 'dashboard'},
        {'label': 'Attendance', 'url_name': 'attendance:offerings', 'icon': 'clipboard-list'},
        {'label': 'Day Book', 'url_name': 'daybook:mine', 'icon': 'book-open'},
        {'label': 'Assessments', 'url_name': 'assessments:offerings', 'icon': 'document-chart'},
        {'label': 'Timetable', 'url_name': 'timetable:teacher-mine', 'icon': 'calendar'},
        {'label': 'Reports', 'url_name': 'reports:home', 'icon': 'chart-bar'},
    ],
    'coordinator': [
        {'label': 'Dashboard', 'url_name': 'dashboard:coordinator', 'icon': 'dashboard'},
        {'label': 'Administration', 'url_name': 'dashboard:admin-portal', 'icon': 'cog'},
        {'label': 'Verify Day Book', 'url_name': 'daybook:verify-queue', 'icon': 'check-circle'},
        {'label': 'Timetable', 'url_name': 'timetable:grid', 'icon': 'calendar'},
        {'label': 'Student Fees', 'url_name': 'finance:students', 'icon': 'banknotes'},
        {'label': 'Reports', 'url_name': 'reports:home', 'icon': 'chart-bar'},
    ],
    'accountant': [
        {'label': 'Dashboard', 'url_name': 'dashboard:accountant', 'icon': 'dashboard'},
        {'label': 'Student Fees', 'url_name': 'finance:students', 'icon': 'banknotes'},
        {'label': 'Challans', 'url_name': 'finance:challans', 'icon': 'document-chart'},
        {'label': 'Administration', 'url_name': 'dashboard:admin-portal', 'icon': 'cog'},
    ],
    'admin': [
        {'label': 'Dashboard', 'url_name': 'dashboard:admin', 'icon': 'dashboard'},
        {'label': 'Administration', 'url_name': 'dashboard:admin-portal', 'icon': 'cog'},
        {'label': 'Verify Day Book', 'url_name': 'daybook:verify-queue', 'icon': 'check-circle'},
        {'label': 'Timetable', 'url_name': 'timetable:grid', 'icon': 'calendar'},
        {'label': 'Student Fees', 'url_name': 'finance:students', 'icon': 'banknotes'},
        {'label': 'Challans', 'url_name': 'finance:challans', 'icon': 'document-chart'},
        {'label': 'Reports', 'url_name': 'reports:home', 'icon': 'chart-bar'},
        {'label': 'Admin Panel', 'url_name': 'admin:index', 'icon': 'lock'},
    ],
}


def role_context(request):
    role = getattr(request, 'role', None)
    role_display = None
    if request.user.is_authenticated:
        role_display = request.user.get_role_display()

    nav_links = []
    for link in NAV_CONFIG.get(role, []):
        try:
            url = reverse(link['url_name'])
        except Exception:
            continue
        nav_links.append(
            {
                **link,
                'url': url,
                'is_active': request.path == url or (
                    url != '/' and request.path.startswith(url)
                ),
            }
        )

    return {
        'role': role,
        'role_display': role_display,
        'nav_links': nav_links,
    }
