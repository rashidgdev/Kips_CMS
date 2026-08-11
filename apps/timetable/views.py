from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy

from apps.academics.models import CourseOffering, Enrollment, Semester
from apps.accounts.models import Roles
from apps.common.crud import CrudCreateView, CrudDeleteView, CrudListView, CrudUpdateView
from apps.common.exports import export_pdf
from apps.common.middleware import get_profile
from apps.common.permissions import role_required

from .forms import RoomForm, TimeSlotForm, TimetableEntryForm
from .models import Room, TimeSlot, TimetableEntry
from .services import build_grid, check_conflicts

_TIMETABLE_PDF_HEADERS = ['Day', 'Time', 'Course', 'Room', 'Teacher']


def _timetable_pdf_rows(entries):
    entries = entries.select_related(
        'time_slot', 'room', 'course_offering__course', 'course_offering__teacher__user'
    ).order_by('time_slot__day_of_week', 'time_slot__start_time')
    return [
        [
            entry.time_slot.get_day_of_week_display(),
            f'{entry.time_slot.start_time_display}-{entry.time_slot.end_time_display}',
            str(entry.course_offering.course),
            str(entry.room),
            entry.course_offering.teacher.user.get_full_name(),
        ]
        for entry in entries
    ]

STAFF_ROLES = (Roles.COORDINATOR, Roles.ADMIN)


# --- Rooms & time slots (setup data) ----------------------------------------

class RoomListView(CrudListView):
    model = Room
    allowed_roles = STAFF_ROLES
    page_title = 'Rooms'
    list_display = [('name', 'Name'), ('building', 'Building'), ('capacity', 'Capacity'), ('room_type', 'Type')]
    add_url_name = 'timetable:room-new'
    edit_url_name = 'timetable:room-edit'
    delete_url_name = 'timetable:room-delete'


class RoomCreateView(CrudCreateView):
    model = Room
    form_class = RoomForm
    allowed_roles = STAFF_ROLES
    page_title = 'Add Room'
    success_url = reverse_lazy('timetable:rooms')
    success_message = 'Room created.'


class RoomUpdateView(CrudUpdateView):
    model = Room
    form_class = RoomForm
    allowed_roles = STAFF_ROLES
    page_title = 'Edit Room'
    success_url = reverse_lazy('timetable:rooms')
    success_message = 'Room updated.'


class RoomDeleteView(CrudDeleteView):
    model = Room
    allowed_roles = STAFF_ROLES
    success_url = reverse_lazy('timetable:rooms')
    success_message = 'Room deleted.'


class TimeSlotListView(CrudListView):
    model = TimeSlot
    allowed_roles = STAFF_ROLES
    page_title = 'Time Slots'
    list_display = [
        ('get_day_of_week_display', 'Day'), ('start_time_display', 'Start'),
        ('end_time_display', 'End'), ('label', 'Label'),
    ]
    add_url_name = 'timetable:timeslot-new'
    edit_url_name = 'timetable:timeslot-edit'
    delete_url_name = 'timetable:timeslot-delete'


class TimeSlotCreateView(CrudCreateView):
    model = TimeSlot
    form_class = TimeSlotForm
    allowed_roles = STAFF_ROLES
    page_title = 'Add Time Slot'
    success_url = reverse_lazy('timetable:timeslots')
    success_message = 'Time slot created.'


class TimeSlotUpdateView(CrudUpdateView):
    model = TimeSlot
    form_class = TimeSlotForm
    allowed_roles = STAFF_ROLES
    page_title = 'Edit Time Slot'
    success_url = reverse_lazy('timetable:timeslots')
    success_message = 'Time slot updated.'


class TimeSlotDeleteView(CrudDeleteView):
    model = TimeSlot
    allowed_roles = STAFF_ROLES
    success_url = reverse_lazy('timetable:timeslots')
    success_message = 'Time slot deleted.'


def _get_semester(semester_id):
    if semester_id:
        return get_object_or_404(Semester, pk=semester_id)
    current = Semester.objects.filter(is_current=True).first()
    return current or Semester.objects.order_by('-start_date').first()


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def semester_grid(request, semester_id=None):
    semester = _get_semester(semester_id)
    semesters = Semester.objects.select_related('program').order_by('-is_current', 'program__name', '-number')

    grid = {'days': [], 'rows': []}
    if semester:
        entries = TimetableEntry.objects.filter(course_offering__semester=semester)
        grid = build_grid(entries)

    return render(
        request,
        'timetable/semester_grid.html',
        {
            'semester': semester,
            'semesters': semesters,
            'grid': grid,
            'pdf_url': reverse('timetable:grid-pdf', args=[semester.pk]) if semester else None,
        },
    )


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def semester_grid_pdf(request, semester_id):
    semester = get_object_or_404(Semester, pk=semester_id)
    entries = TimetableEntry.objects.filter(course_offering__semester=semester)
    return export_pdf(
        f'timetable_{semester.pk}', f'Timetable - {semester}',
        _TIMETABLE_PDF_HEADERS, _timetable_pdf_rows(entries),
    )


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def schedule_entry(request, semester_id):
    semester = get_object_or_404(Semester, pk=semester_id)
    offerings = CourseOffering.objects.filter(semester=semester, is_active=True).select_related(
        'course', 'teacher__user'
    )

    if request.method == 'POST':
        form = TimetableEntryForm(request.POST, course_offering_queryset=offerings)
        if form.is_valid():
            conflicts = check_conflicts(
                form.cleaned_data['course_offering'],
                form.cleaned_data['room'],
                form.cleaned_data['time_slot'],
            )
            if conflicts:
                for error in conflicts:
                    messages.error(request, error)
            else:
                entry = form.save(commit=False)
                entry.created_by = request.user
                entry.save()
                messages.success(request, 'Class scheduled.')
                return redirect('timetable:grid-for-semester', semester_id=semester.pk)
    else:
        form = TimetableEntryForm(course_offering_queryset=offerings)

    return render(
        request, 'timetable/schedule_form.html', {'semester': semester, 'form': form}
    )


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def unschedule_entry(request, entry_id):
    entry = get_object_or_404(TimetableEntry, pk=entry_id)
    semester_id = entry.course_offering.semester_id
    if request.method == 'POST':
        entry.delete()
        messages.success(request, 'Class removed from timetable.')
    return redirect('timetable:grid-for-semester', semester_id=semester_id)


def _teacher_current_entries(profile):
    return TimetableEntry.objects.filter(
        course_offering__teacher=profile, course_offering__semester__is_current=True
    )


def _student_current_entries(profile):
    return TimetableEntry.objects.filter(
        course_offering__enrollments__student=profile,
        course_offering__enrollments__status=Enrollment.Status.ENROLLED,
    ).distinct()


@role_required(Roles.TEACHER, Roles.HOD)
def teacher_timetable(request):
    profile = get_profile(request)
    grid = build_grid(_teacher_current_entries(profile))
    return render(
        request, 'timetable/my_timetable.html',
        {'grid': grid, 'title': 'My Timetable', 'pdf_url': reverse('timetable:teacher-mine-pdf')},
    )


@role_required(Roles.TEACHER, Roles.HOD)
def teacher_timetable_pdf(request):
    profile = get_profile(request)
    return export_pdf(
        'my_timetable', f'Timetable - {profile}',
        _TIMETABLE_PDF_HEADERS, _timetable_pdf_rows(_teacher_current_entries(profile)),
    )


@role_required(Roles.STUDENT)
def student_timetable(request):
    profile = get_profile(request)
    grid = build_grid(_student_current_entries(profile))
    return render(
        request, 'timetable/my_timetable.html',
        {'grid': grid, 'title': 'My Timetable', 'pdf_url': reverse('timetable:student-mine-pdf')},
    )


@role_required(Roles.STUDENT)
def student_timetable_pdf(request):
    profile = get_profile(request)
    return export_pdf(
        'my_timetable', f'Timetable - {profile}',
        _TIMETABLE_PDF_HEADERS, _timetable_pdf_rows(_student_current_entries(profile)),
    )
