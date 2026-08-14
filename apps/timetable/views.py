import datetime

from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy

from apps.academics.models import CourseOffering, Enrollment, Semester
from apps.accounts.models import Roles
from apps.common.crud import CrudCreateView, CrudDeleteView, CrudListView, CrudUpdateView
from apps.common.middleware import get_profile
from apps.common.permissions import role_required

from .forms import RoomForm, TimeSlotForm, TimeSlotGeneratorForm, TimeSlotResizeForm, TimetableEntryForm
from .grid_pdf import render_timetable_grid_pdf
from .models import Room, TimeSlot, TimetableEntry
from .services import auto_schedule_semester, build_grid, check_conflicts, generate_time_slots, resize_day_slots

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
    bulk_delete_url_name = 'timetable:timeslot-bulk-delete'
    row_actions = [{'url_name': 'timetable:timeslot-resize', 'label': 'Resize'}]
    extra_actions = [{'url_name': 'timetable:timeslot-generate', 'label': 'Generate Time Slots', 'icon': 'clock'}]


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


@role_required(*STAFF_ROLES)
def timeslot_bulk_delete(request):
    if request.method != 'POST':
        return redirect('timetable:timeslots')

    pks = request.POST.getlist('pks')
    if not pks:
        messages.error(request, 'No time slots were selected.')
        return redirect('timetable:timeslots')

    deleted_count = 0
    blocked = []
    for slot in TimeSlot.objects.filter(pk__in=pks):
        try:
            slot.delete()
            deleted_count += 1
        except ProtectedError:
            blocked.append(str(slot))

    if deleted_count:
        messages.success(request, f'{deleted_count} time slot(s) deleted.')
    if blocked:
        messages.warning(
            request,
            f'{len(blocked)} time slot(s) are still in use by scheduled classes and were not deleted: '
            + ', '.join(blocked),
        )
    return redirect('timetable:timeslots')


@role_required(*STAFF_ROLES)
def timeslot_resize(request, pk):
    slot = get_object_or_404(TimeSlot, pk=pk)
    current_minutes = int(
        (datetime.datetime.combine(datetime.date.today(), slot.end_time)
         - datetime.datetime.combine(datetime.date.today(), slot.start_time)).total_seconds() // 60
    )

    if request.method == 'POST':
        form = TimeSlotResizeForm(request.POST)
        if form.is_valid():
            new_slots, remapped_count = resize_day_slots(
                slot.day_of_week, form.cleaned_data['lecture_duration_minutes']
            )
            messages.success(
                request,
                f'{slot.get_day_of_week_display()} slots resized to '
                f'{form.cleaned_data["lecture_duration_minutes"]} minutes each '
                f'({len(new_slots)} slot(s), {remapped_count} scheduled class(es) moved to their new slot).',
            )
            return redirect('timetable:timeslots')
    else:
        form = TimeSlotResizeForm(initial={'lecture_duration_minutes': current_minutes})

    return render(request, 'common/generic_form.html', {
        'form': form,
        'page_title': f'Resize {slot.get_day_of_week_display()} Slots',
        'cancel_url': reverse('timetable:timeslots'),
    })


@role_required(*STAFF_ROLES)
def timeslot_generate(request):
    if request.method == 'POST':
        form = TimeSlotGeneratorForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            created, skipped = generate_time_slots(
                days=[int(d) for d in data['days']],
                day_start_time=data['day_start_time'],
                lecture_duration_minutes=data['lecture_duration_minutes'],
                number_of_lectures=data['number_of_lectures'],
                breaks=data['breaks'],
            )
            if created:
                messages.success(
                    request,
                    f'{len(created)} time slot(s) created - each lecture is '
                    f'{data["lecture_duration_minutes"]} minutes long.',
                )
            if skipped:
                messages.info(request, f'{len(skipped)} time slot(s) already existed and were left as-is.')
            if not created and not skipped:
                messages.warning(request, 'No days were selected - nothing was generated.')
            return redirect('timetable:timeslots')
    else:
        form = TimeSlotGeneratorForm()

    return render(request, 'timetable/timeslot_generate.html', {'form': form})


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
    grid = build_grid(entries)
    return render_timetable_grid_pdf(grid, 'Timetable', subtitle=str(semester))


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


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def auto_schedule_semester_view(request, semester_id):
    semester = get_object_or_404(Semester, pk=semester_id)
    if request.method == 'POST':
        created, unscheduled = auto_schedule_semester(semester, created_by=request.user)
        if created:
            messages.success(request, f'{len(created)} class(es) auto-scheduled.')
        if unscheduled:
            names = ', '.join(str(offering) for offering, _reason in unscheduled)
            messages.warning(
                request,
                f'{len(unscheduled)} class(es) could not be auto-scheduled - no free room/time-slot '
                f'combination was available: {names}. Add more rooms or time slots, or schedule them manually.',
            )
        if not created and not unscheduled:
            messages.info(request, 'Nothing to schedule - every course offering already has its required classes.')
    return redirect('timetable:grid-for-semester', semester_id=semester.pk)


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
    grid = build_grid(_teacher_current_entries(profile))
    return render_timetable_grid_pdf(grid, 'My Timetable', subtitle=str(profile))


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
    grid = build_grid(_student_current_entries(profile))
    return render_timetable_grid_pdf(grid, 'My Timetable', subtitle=str(profile))
