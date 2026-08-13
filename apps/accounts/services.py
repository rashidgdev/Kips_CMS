"""
Business logic shared between the Django template views (views.py) and the
REST API (api_views.py), so neither duplicates the other.
"""
from django.db.models import Q

from .models import User


def filter_people(role=None, department=None, query=None):
    """Powers both the People directory template and its API equivalent.
    A student's "department" is read through their program (StaffProfile
    has no department of its own - coordinator/accountant/admin are
    campus-wide, not tied to one)."""
    users = User.objects.select_related(
        'student_profile__program__department', 'teacher_profile__department', 'staff_profile'
    ).order_by('role', 'first_name')

    if role:
        users = users.filter(role=role)

    if department:
        users = users.filter(
            Q(teacher_profile__department_id=department)
            | Q(student_profile__program__department_id=department)
        )

    if query:
        users = users.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(student_profile__roll_number__icontains=query)
            | Q(teacher_profile__employee_id__icontains=query)
            | Q(staff_profile__employee_id__icontains=query)
        )

    return users.distinct()
