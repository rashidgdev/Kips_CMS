from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from apps.accounts.models import Roles, StudentProfile
from apps.common.crud import CrudCreateView, CrudDeleteView, CrudListView, CrudUpdateView
from apps.common.permissions import role_required

from .forms import CourseForm, CourseOfferingForm, EnrollmentForm, ProgramForm, SemesterForm
from .models import Course, CourseOffering, Enrollment, Program, Semester
from .services import bulk_enroll_by_offering, bulk_enroll_by_student

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
        ('code', 'Code'), ('title', 'Title'), ('program', 'Program'), ('semester_number', 'Sem #'),
        ('credit_hours', 'Credit Hrs'), ('course_type', 'Type'), ('is_active', 'Active'),
    ]
    add_url_name = 'academics:course-new'
    edit_url_name = 'academics:course-edit'
    delete_url_name = 'academics:course-delete'
    filter_fields = [
        ('program', 'Program', Program.objects.all()),
        ('semester_number', 'Semester #', None),
    ]
    search_fields = ['code', 'title']
    search_placeholder = 'Course code or name...'

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
    template_name = 'academics/courseoffering_form.html'

    def form_valid(self, form):
        form.instance.assigned_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['programs'] = Program.objects.all()
        context['selected_program_id'] = self.request.POST.get('program_filter', '')
        return context


class CourseOfferingUpdateView(CrudUpdateView):
    model = CourseOffering
    form_class = CourseOfferingForm
    allowed_roles = STAFF_ROLES
    page_title = 'Edit Faculty Assignment'
    success_url = reverse_lazy('academics:offerings')
    success_message = 'Faculty assignment updated.'
    template_name = 'academics/courseoffering_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['programs'] = Program.objects.all()
        context['selected_program_id'] = (
            self.request.POST.get('program_filter') or str(self.object.course.program_id)
        )
        return context


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


# --- Bulk enrollment ---------------------------------------------------------
# The generic Enrollment CRUD above handles one student/one offering at a
# time, which is too slow when registering a whole class or building one
# student's full course load. These two screens do the same underlying
# Enrollment.objects.create in bulk.

@role_required(*STAFF_ROLES)
def enroll_by_offering(request):
    """Pick one course offering, then enroll many students into it at once."""
    offerings = CourseOffering.objects.filter(is_active=True).select_related(
        'course', 'semester', 'course__program'
    ).order_by('-semester__is_current', 'semester', 'course')
    selected_offering = None
    students = []
    already_enrolled_ids = set()

    offering_id = request.POST.get('offering') or request.GET.get('offering')
    if offering_id:
        selected_offering = get_object_or_404(CourseOffering, pk=offering_id)
        already_enrolled_ids = set(selected_offering.enrollments.values_list('student_id', flat=True))
        students = StudentProfile.objects.filter(
            program=selected_offering.course.program,
            current_semester=selected_offering.semester,
            section=selected_offering.section,
            status=StudentProfile.Status.ACTIVE,
        ).select_related('user').order_by('roll_number')

    if request.method == 'POST':
        student_ids = {int(sid) for sid in request.POST.getlist('student_ids')}
        if not selected_offering:
            messages.error(request, 'Select a course offering first.')
        elif not student_ids:
            messages.error(request, 'Select at least one student to enroll.')
        else:
            enrolled_count, skipped_count = bulk_enroll_by_offering(selected_offering, student_ids)
            messages.success(request, f'Enrolled {enrolled_count} student(s) in {selected_offering}.')
            if skipped_count:
                messages.warning(
                    request,
                    f'{skipped_count} student(s) could not be enrolled - the section is at capacity '
                    f'({selected_offering.max_seats} seats).',
                )
            return redirect(f'{request.path}?offering={selected_offering.id}')

    return render(request, 'academics/enroll_by_offering.html', {
        'offerings': offerings,
        'selected_offering': selected_offering,
        'students': students,
        'already_enrolled_ids': already_enrolled_ids,
    })


@role_required(*STAFF_ROLES)
def enroll_by_student(request):
    """Pick one student, then enroll them into many course offerings at once."""
    students = StudentProfile.objects.select_related('user', 'program').order_by('roll_number')
    selected_student = None
    offerings = []
    already_enrolled_ids = set()

    student_id = request.POST.get('student') or request.GET.get('student')
    if student_id:
        selected_student = get_object_or_404(StudentProfile, pk=student_id)
        already_enrolled_ids = set(selected_student.enrollments.values_list('course_offering_id', flat=True))
        offerings = CourseOffering.objects.filter(
            course__program=selected_student.program, is_active=True
        )
        # Scope to the student's own current semester when known - otherwise
        # every semester the program has ever run would show, which is how
        # this used to work for everyone and is why picking the right
        # section's offering was error-prone once a semester had more than
        # one.
        if selected_student.current_semester_id:
            offerings = offerings.filter(semester=selected_student.current_semester)
        offerings = offerings.select_related('course', 'semester').order_by(
            '-semester__is_current', 'semester', 'course'
        )

    if request.method == 'POST':
        offering_ids = {int(oid) for oid in request.POST.getlist('offering_ids')}
        if not selected_student:
            messages.error(request, 'Select a student first.')
        elif not offering_ids:
            messages.error(request, 'Select at least one course offering.')
        else:
            enrolled_count = bulk_enroll_by_student(selected_student, offering_ids)
            messages.success(request, f'Enrolled {selected_student} in {enrolled_count} course(s).')
            return redirect(f'{request.path}?student={selected_student.id}')

    return render(request, 'academics/enroll_by_student.html', {
        'students': students,
        'selected_student': selected_student,
        'offerings': offerings,
        'already_enrolled_ids': already_enrolled_ids,
    })
