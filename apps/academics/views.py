from django.urls import reverse_lazy

from apps.accounts.models import Roles
from apps.common.crud import CrudCreateView, CrudDeleteView, CrudListView, CrudUpdateView

from .forms import CourseForm, CourseOfferingForm, EnrollmentForm, ProgramForm, SemesterForm
from .models import Course, CourseOffering, Enrollment, Program, Semester

STAFF_ROLES = (Roles.COORDINATOR, Roles.ADMIN)


# --- Programs ------------------------------------------------------------

class ProgramListView(CrudListView):
    model = Program
    allowed_roles = STAFF_ROLES
    page_title = 'Programs'
    list_display = [
        ('code', 'Code'), ('name', 'Name'), ('department', 'Department'),
        ('degree_level', 'Level'), ('total_semesters', 'Semesters'), ('is_active', 'Active'),
    ]
    add_url_name = 'academics:program-new'
    edit_url_name = 'academics:program-edit'
    delete_url_name = 'academics:program-delete'


class ProgramCreateView(CrudCreateView):
    model = Program
    form_class = ProgramForm
    allowed_roles = STAFF_ROLES
    page_title = 'Add Program'
    success_url = reverse_lazy('academics:programs')
    success_message = 'Program created.'


class ProgramUpdateView(CrudUpdateView):
    model = Program
    form_class = ProgramForm
    allowed_roles = STAFF_ROLES
    page_title = 'Edit Program'
    success_url = reverse_lazy('academics:programs')
    success_message = 'Program updated.'


class ProgramDeleteView(CrudDeleteView):
    model = Program
    allowed_roles = STAFF_ROLES
    success_url = reverse_lazy('academics:programs')
    success_message = 'Program deleted.'


# --- Semesters ------------------------------------------------------------

class SemesterListView(CrudListView):
    model = Semester
    allowed_roles = STAFF_ROLES
    page_title = 'Semesters'
    list_display = [
        ('program', 'Program'), ('number', '#'), ('academic_year', 'Academic Year'),
        ('start_date', 'Start'), ('end_date', 'End'), ('is_current', 'Current'),
    ]
    add_url_name = 'academics:semester-new'
    edit_url_name = 'academics:semester-edit'
    delete_url_name = 'academics:semester-delete'

    def get_queryset(self):
        return super().get_queryset().select_related('program')


class SemesterCreateView(CrudCreateView):
    model = Semester
    form_class = SemesterForm
    allowed_roles = STAFF_ROLES
    page_title = 'Add Semester'
    success_url = reverse_lazy('academics:semesters')
    success_message = 'Semester created.'


class SemesterUpdateView(CrudUpdateView):
    model = Semester
    form_class = SemesterForm
    allowed_roles = STAFF_ROLES
    page_title = 'Edit Semester'
    success_url = reverse_lazy('academics:semesters')
    success_message = 'Semester updated.'


class SemesterDeleteView(CrudDeleteView):
    model = Semester
    allowed_roles = STAFF_ROLES
    success_url = reverse_lazy('academics:semesters')
    success_message = 'Semester deleted.'


# --- Courses ------------------------------------------------------------

class CourseListView(CrudListView):
    model = Course
    allowed_roles = STAFF_ROLES
    page_title = 'Courses'
    list_display = [
        ('code', 'Code'), ('title', 'Title'), ('program', 'Program'),
        ('credit_hours', 'Credit Hrs'), ('course_type', 'Type'), ('is_active', 'Active'),
    ]
    add_url_name = 'academics:course-new'
    edit_url_name = 'academics:course-edit'
    delete_url_name = 'academics:course-delete'

    def get_queryset(self):
        return super().get_queryset().select_related('program')


class CourseCreateView(CrudCreateView):
    model = Course
    form_class = CourseForm
    allowed_roles = STAFF_ROLES
    page_title = 'Add Course'
    success_url = reverse_lazy('academics:courses')
    success_message = 'Course created.'


class CourseUpdateView(CrudUpdateView):
    model = Course
    form_class = CourseForm
    allowed_roles = STAFF_ROLES
    page_title = 'Edit Course'
    success_url = reverse_lazy('academics:courses')
    success_message = 'Course updated.'


class CourseDeleteView(CrudDeleteView):
    model = Course
    allowed_roles = STAFF_ROLES
    success_url = reverse_lazy('academics:courses')
    success_message = 'Course deleted.'


# --- Course Offerings (faculty assignment) --------------------------------

class CourseOfferingListView(CrudListView):
    model = CourseOffering
    allowed_roles = STAFF_ROLES
    page_title = 'Faculty Assignments'
    list_display = [
        ('course', 'Course'), ('semester', 'Semester'), ('section', 'Section'),
        ('teacher', 'Teacher'), ('max_seats', 'Max Seats'), ('is_active', 'Active'),
    ]
    add_url_name = 'academics:offering-new'
    edit_url_name = 'academics:offering-edit'
    delete_url_name = 'academics:offering-delete'

    def get_queryset(self):
        return super().get_queryset().select_related('course', 'semester', 'teacher__user')


class CourseOfferingCreateView(CrudCreateView):
    model = CourseOffering
    form_class = CourseOfferingForm
    allowed_roles = STAFF_ROLES
    page_title = 'Assign Course to Faculty'
    success_url = reverse_lazy('academics:offerings')
    success_message = 'Course assigned to faculty.'

    def form_valid(self, form):
        form.instance.assigned_by = self.request.user
        return super().form_valid(form)


class CourseOfferingUpdateView(CrudUpdateView):
    model = CourseOffering
    form_class = CourseOfferingForm
    allowed_roles = STAFF_ROLES
    page_title = 'Edit Faculty Assignment'
    success_url = reverse_lazy('academics:offerings')
    success_message = 'Faculty assignment updated.'


class CourseOfferingDeleteView(CrudDeleteView):
    model = CourseOffering
    allowed_roles = STAFF_ROLES
    success_url = reverse_lazy('academics:offerings')
    success_message = 'Faculty assignment removed.'


# --- Enrollments ------------------------------------------------------------

class EnrollmentListView(CrudListView):
    model = Enrollment
    allowed_roles = STAFF_ROLES
    page_title = 'Enrollments'
    list_display = [
        ('student', 'Student'), ('course_offering', 'Course Offering'),
        ('status', 'Status'), ('enrolled_at', 'Enrolled At'),
    ]
    add_url_name = 'academics:enrollment-new'
    edit_url_name = 'academics:enrollment-edit'
    delete_url_name = 'academics:enrollment-delete'

    def get_queryset(self):
        return super().get_queryset().select_related(
            'student__user', 'course_offering__course', 'course_offering__semester'
        )


class EnrollmentCreateView(CrudCreateView):
    model = Enrollment
    form_class = EnrollmentForm
    allowed_roles = STAFF_ROLES
    page_title = 'Enroll Student'
    success_url = reverse_lazy('academics:enrollments')
    success_message = 'Student enrolled.'


class EnrollmentUpdateView(CrudUpdateView):
    model = Enrollment
    form_class = EnrollmentForm
    allowed_roles = STAFF_ROLES
    page_title = 'Edit Enrollment'
    success_url = reverse_lazy('academics:enrollments')
    success_message = 'Enrollment updated.'


class EnrollmentDeleteView(CrudDeleteView):
    model = Enrollment
    allowed_roles = STAFF_ROLES
    success_url = reverse_lazy('academics:enrollments')
    success_message = 'Enrollment removed.'
