import datetime

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


def generate_time_slots(days, day_start_time, lecture_duration_minutes, number_of_lectures, breaks=None):
    """Builds `number_of_lectures` TimeSlots (Period 1, Period 2, ...) per
    selected day, instead of the user adding each one by hand. Every lecture
    is the same length, but breaks don't have to fall after every lecture
    and don't have to be the same length - `breaks` is a list of
    (after_lecture, duration_minutes) pairs, e.g. [(2, 15), (4, 30)] means a
    15 min break after lecture 2 and a 30 min break after lecture 4, with
    lectures 1-2, 3-4, and 5+ otherwise back-to-back. Reuses an existing
    slot instead of erroring if it already exists (e.g. re-running this
    after adding a day), so it's safe to run more than once."""
    break_minutes_by_lecture = dict(breaks or [])
    today = datetime.date.today()
    created, skipped = [], []

    for day in days:
        current_start = day_start_time
        for period_number in range(1, number_of_lectures + 1):
            current_end = (
                datetime.datetime.combine(today, current_start) + datetime.timedelta(minutes=lecture_duration_minutes)
            ).time()
            slot, was_created = TimeSlot.objects.get_or_create(
                day_of_week=day,
                start_time=current_start,
                end_time=current_end,
                defaults={'label': f'Period {period_number}'},
            )
            (created if was_created else skipped).append(slot)

            break_minutes = break_minutes_by_lecture.get(period_number, 0)
            next_start_dt = datetime.datetime.combine(today, current_end) + datetime.timedelta(minutes=break_minutes)
            current_start = next_start_dt.time()

    return created, skipped


def _minutes_between(start_time, end_time):
    today = datetime.date.today()
    delta = datetime.datetime.combine(today, end_time) - datetime.datetime.combine(today, start_time)
    return int(delta.total_seconds() // 60)


MAX_BREAK_MINUTES = 120  # a school break is never longer than this in practice


def build_grid(entries):
    """Builds a day x period grid for template rendering from a TimetableEntry
    queryset. Any genuine time gap between one period's end and the next
    period's start (e.g. left by the "Generate Time Slots" break settings)
    is surfaced as its own labeled break row spanning every day column,
    instead of being an invisible gap in the schedule.

    The period list is a union of every TimeSlot's (start, end) across every
    day (not just the days actually being viewed), because that's what lets
    a day with no class in some period still render an empty cell in the
    right row. If two days' periods were configured at very different times
    (e.g. one day starts mid-afternoon, another starts in the morning), the
    "gap" between them in that merged list isn't a real break - it's just
    where the union jumps from one day's schedule to another's. Capping at
    MAX_BREAK_MINUTES keeps those artifacts from being mislabeled as one
    giant break while still catching every plausible real one."""
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
    rows = []
    for index, period in enumerate(periods):
        cells = []
        for day_value, day_label in days:
            key = (day_value, period['start_time'], period['end_time'])
            cells.append({'day': day_value, 'day_label': day_label, 'entry': entry_map.get(key)})
        rows.append({'type': 'period', 'period': period, 'cells': cells})

        if index + 1 < len(periods):
            next_period = periods[index + 1]
            gap_minutes = _minutes_between(period['end_time'], next_period['start_time'])
            if 0 < gap_minutes <= MAX_BREAK_MINUTES:
                rows.append(
                    {
                        'type': 'break',
                        'start_time': period['end_time'],
                        'end_time': next_period['start_time'],
                        'duration_minutes': gap_minutes,
                    }
                )

    return {'days': days, 'rows': rows}
