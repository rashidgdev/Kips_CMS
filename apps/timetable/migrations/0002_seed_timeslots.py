import datetime

from django.db import migrations

# Standard Mon-Fri periods; Saturday is left available for manual scheduling if needed.
PERIODS = [
    ('Period 1', datetime.time(9, 0), datetime.time(10, 0)),
    ('Period 2', datetime.time(10, 0), datetime.time(11, 0)),
    ('Period 3', datetime.time(11, 0), datetime.time(12, 0)),
    ('Period 4', datetime.time(13, 0), datetime.time(14, 0)),
    ('Period 5', datetime.time(14, 0), datetime.time(15, 0)),
]
WEEKDAYS = [1, 2, 3, 4, 5]  # Monday-Friday, matches TimeSlot.DayOfWeek values


def seed_timeslots(apps, schema_editor):
    TimeSlot = apps.get_model('timetable', 'TimeSlot')
    for day in WEEKDAYS:
        for label, start_time, end_time in PERIODS:
            TimeSlot.objects.get_or_create(
                day_of_week=day, start_time=start_time, end_time=end_time, defaults={'label': label}
            )


def unseed_timeslots(apps, schema_editor):
    TimeSlot = apps.get_model('timetable', 'TimeSlot')
    TimeSlot.objects.filter(day_of_week__in=WEEKDAYS, label__in=[p[0] for p in PERIODS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_timeslots, unseed_timeslots),
    ]
