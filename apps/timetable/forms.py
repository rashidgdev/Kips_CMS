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
    """Generates a full day's worth of back-to-back lecture time slots
    instead of adding each one by hand."""

    days = forms.MultipleChoiceField(
        choices=TimeSlot.DayOfWeek.choices,
        initial=[c[0] for c in TimeSlot.DayOfWeek.choices],
        widget=forms.CheckboxSelectMultiple,
        label='Working days',
    )
    day_start_time = forms.TimeField(label='Start of working day', widget=forms.TimeInput(attrs={'type': 'time'}))
    day_end_time = forms.TimeField(label='End of working day', widget=forms.TimeInput(attrs={'type': 'time'}))
    lecture_duration_minutes = forms.IntegerField(label='Length of each lecture (minutes)', min_value=5, initial=50)
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
        duration = cleaned.get('lecture_duration_minutes')
        count = cleaned.get('number_of_lectures')
        break_minutes = cleaned.get('break_minutes') or 0

        if start and end and duration and count:
            if end <= start:
                raise forms.ValidationError('End of working day must be after the start of the working day.')

            total_minutes = duration * count + break_minutes * (count - 1)
            last_end = (
                datetime.datetime.combine(datetime.date.today(), start) + datetime.timedelta(minutes=total_minutes)
            ).time()
            if last_end > end:
                raise forms.ValidationError(
                    f'{count} lectures of {duration} min (plus {break_minutes} min breaks) starting at '
                    f'{start.strftime("%I:%M %p").lstrip("0")} would end at '
                    f'{last_end.strftime("%I:%M %p").lstrip("0")}, which is after the working day ends at '
                    f'{end.strftime("%I:%M %p").lstrip("0")}. Reduce the number of lectures, shorten the lecture '
                    'or break length, or extend the working day.'
                )
        return cleaned
