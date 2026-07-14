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
