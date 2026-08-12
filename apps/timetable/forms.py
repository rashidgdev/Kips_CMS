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


MAX_BREAKS = 5


class TimeSlotGeneratorForm(TailwindFormMixin, forms.Form):
    """Generates a full day's worth of lecture time slots instead of adding
    each one by hand. Lecture length is not entered directly - it's computed
    by evenly dividing the working day span (minus any breaks) across the
    requested number of lectures. Breaks don't have to fall after every
    lecture and don't have to be the same length - each of up to
    MAX_BREAKS break rows independently says "after lecture N, break for
    X minutes" (e.g. a 15 min break after lecture 2, a 30 min lunch break
    after lecture 4)."""

    days = forms.MultipleChoiceField(
        choices=TimeSlot.DayOfWeek.choices,
        initial=[c[0] for c in TimeSlot.DayOfWeek.choices],
        widget=forms.CheckboxSelectMultiple,
        label='Working days',
    )
    day_start_time = forms.TimeField(label='Start of working day', widget=forms.TimeInput(attrs={'type': 'time'}))
    day_end_time = forms.TimeField(label='End of working day', widget=forms.TimeInput(attrs={'type': 'time'}))
    number_of_lectures = forms.IntegerField(label='Number of lectures per day', min_value=1, initial=6)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['days'].widget.attrs.pop('class', None)
        for i in range(1, MAX_BREAKS + 1):
            self.fields[f'break_after_{i}'] = forms.IntegerField(
                label='After lecture', min_value=1, required=False,
                widget=forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            )
            self.fields[f'break_duration_{i}'] = forms.IntegerField(
                label='Break length (minutes)', min_value=1, required=False,
                widget=forms.NumberInput(attrs={'class': INPUT_CLASSES}),
            )

    @property
    def break_rows(self):
        """Pairs up the break_after_N/break_duration_N fields so the template
        can render them as MAX_BREAKS simple two-input rows."""
        return [(self[f'break_after_{i}'], self[f'break_duration_{i}']) for i in range(1, MAX_BREAKS + 1)]

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('day_start_time')
        end = cleaned.get('day_end_time')
        count = cleaned.get('number_of_lectures')

        breaks = []
        seen_positions = set()
        for i in range(1, MAX_BREAKS + 1):
            after = cleaned.get(f'break_after_{i}')
            duration = cleaned.get(f'break_duration_{i}')
            if after is None and duration is None:
                continue
            if after is None or duration is None:
                raise forms.ValidationError(
                    f'Break {i}: fill in both "after lecture" and "break length", or leave both blank.'
                )
            if count and after >= count:
                raise forms.ValidationError(
                    f'Break {i}: "after lecture {after}" is not valid for {count} lecture(s) - a break must '
                    'fall after one of the lectures and before the last one.'
                )
            if after in seen_positions:
                raise forms.ValidationError(
                    f'Two breaks are both set to fall after lecture {after} - combine them into one break.'
                )
            seen_positions.add(after)
            breaks.append((after, duration))
        breaks.sort(key=lambda pair: pair[0])
        cleaned['breaks'] = breaks

        if start and end and count:
            if end <= start:
                raise forms.ValidationError('End of working day must be after the start of the working day.')

            span_minutes = (
                datetime.datetime.combine(datetime.date.today(), end)
                - datetime.datetime.combine(datetime.date.today(), start)
            ).total_seconds() / 60
            break_total = sum(duration for _after, duration in breaks)
            available_minutes = span_minutes - break_total

            lecture_duration_minutes = int(available_minutes // count)
            if lecture_duration_minutes < 5:
                raise forms.ValidationError(
                    f'Splitting {start.strftime("%I:%M %p").lstrip("0")}-{end.strftime("%I:%M %p").lstrip("0")} '
                    f'into {count} lectures with {break_total} min of breaks leaves less than 5 minutes per '
                    'lecture. Reduce the number of lectures or break time, or extend the working day.'
                )
            cleaned['lecture_duration_minutes'] = lecture_duration_minutes
        return cleaned
