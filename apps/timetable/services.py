from django.db.models import Q

from .models import TimeSlot, TimetableEntry


def check_conflicts(course_offering, room, time_slot, exclude_entry_id=None):
    """Returns a list of human-readable conflict errors, empty if the slot is free.

    Room conflicts are checked globally (a room can only ever host one class in a
    given weekly slot). Teacher conflicts are checked against any *currently
    running* semester plus the semester being scheduled, since several
    semesters/programs run concurrently and a teacher can't be in two places
    at once regardless of which semester each class belongs to.
    """
    errors = []

    room_clash = TimetableEntry.objects.filter(room=room, time_slot=time_slot)
    if exclude_entry_id:
        room_clash = room_clash.exclude(pk=exclude_entry_id)
    room_entry = room_clash.select_related('course_offering__course').first()
    if room_entry:
        errors.append(f'Room {room} is already booked at {time_slot} for {room_entry.course_offering.course}.')

    concurrent_semesters = Q(course_offering__semester__is_current=True) | Q(
        course_offering__semester=course_offering.semester
    )
    teacher_clash = TimetableEntry.objects.filter(
        concurrent_semesters, time_slot=time_slot, course_offering__teacher=course_offering.teacher
    )
    if exclude_entry_id:
        teacher_clash = teacher_clash.exclude(pk=exclude_entry_id)
    teacher_entry = teacher_clash.select_related('course_offering__course').first()
    if teacher_entry:
        errors.append(
            f'{course_offering.teacher} is already scheduled at {time_slot} for {teacher_entry.course_offering.course}.'
        )

    return errors


def build_grid(entries):
    """Builds a day x period grid for template rendering from a TimetableEntry queryset."""
    entries = entries.select_related(
        'time_slot', 'room', 'course_offering__course', 'course_offering__teacher__user'
    )

    periods = []
    seen = set()
    for slot in TimeSlot.objects.order_by('start_time', 'end_time'):
        key = (slot.start_time, slot.end_time)
        if key not in seen:
            seen.add(key)
            periods.append({'start_time': slot.start_time, 'end_time': slot.end_time, 'label': slot.label})

    entry_map = {
        (e.time_slot.day_of_week, e.time_slot.start_time, e.time_slot.end_time): e for e in entries
    }

    days = TimeSlot.DayOfWeek.choices
    grid = []
    for period in periods:
        row = {'period': period, 'cells': []}
        for day_value, day_label in days:
            key = (day_value, period['start_time'], period['end_time'])
            row['cells'].append({'day': day_value, 'day_label': day_label, 'entry': entry_map.get(key)})
        grid.append(row)

    return {'days': days, 'rows': grid}
