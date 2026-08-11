import datetime

from django import forms

from apps.common.forms import INPUT_CLASSES, TailwindFormMixin

from .models import Room, TimeSlot, TimetableEntry


class TimetableEntryForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = ['course_offering', 'room', 'time_slot']
        widgets = {
            'course_offering': forms.Select(attrs={'class': INPUT_CLASSES}),
            'room': forms.Select(attrs={'class': INPUT_CLASSES}),
            'time_slot': forms.Select(attrs={'class': INPUT_CLASSES}),
        }

    def __init__(self, *args, course_offering_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if course_offering_queryset is not None:
            self.fields['course_offering'].queryset = course_offering_queryset

    def validate_unique(self):
        # Skip the ModelForm's automatic (room, time_slot) uniqueness check -
        # the view calls services.check_conflicts() instead, which reports
        # both room and teacher conflicts with a specific, friendly message.
        pass


class RoomForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'building', 'capacity', 'room_type']


class TimeSlotForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['day_of_week', 'start_time', 'end_time', 'label']


class TimeSlotGeneratorForm(TailwindFormMixin, forms.Form):
    """Generates a full day's worth of lecture time slots instead of adding
    each one by hand. Lecture length is not entered directly - it's computed
    by evenly dividing the working day span (minus any breaks) across the
    requested number of lectures."""

    days = forms.MultipleChoiceField(
        choices=TimeSlot.DayOfWeek.choices,
        initial=[c[0] for c in TimeSlot.DayOfWeek.choices],
        widget=forms.CheckboxSelectMultiple,
        label='Working days',
    )
    day_start_time = forms.TimeField(label='Start of working day', widget=forms.TimeInput(attrs={'type': 'time'}))
    day_end_time = forms.TimeField(label='End of working day', widget=forms.TimeInput(attrs={'type': 'time'}))
    number_of_lectures = forms.IntegerField(label='Number of lectures per day', min_value=1, initial=6)
    break_minutes = forms.IntegerField(
        label='Break between lectures (minutes)', min_value=0, initial=0, required=False,
        help_text='Optional - leave as 0 for back-to-back lectures with no gap.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['days'].widget.attrs.pop('class', None)

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('day_start_time')
        end = cleaned.get('day_end_time')
        count = cleaned.get('number_of_lectures')
        break_minutes = cleaned.get('break_minutes') or 0

        if start and end and count:
            if end <= start:
                raise forms.ValidationError('End of working day must be after the start of the working day.')

            span_minutes = (
                datetime.datetime.combine(datetime.date.today(), end)
                - datetime.datetime.combine(datetime.date.today(), start)
            ).total_seconds() / 60
            break_total = break_minutes * (count - 1)
            available_minutes = span_minutes - break_total

            lecture_duration_minutes = int(available_minutes // count)
            if lecture_duration_minutes < 5:
                raise forms.ValidationError(
                    f'Splitting {start.strftime("%I:%M %p").lstrip("0")}-{end.strftime("%I:%M %p").lstrip("0")} '
                    f'into {count} lectures with {break_minutes} min breaks between them leaves less than 5 '
                    'minutes per lecture. Reduce the number of lectures or breaks, or extend the working day.'
                )
            cleaned['lecture_duration_minutes'] = lecture_duration_minutes
        return cleaned
