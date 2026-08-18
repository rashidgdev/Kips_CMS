import datetime

from django import forms

from apps.common.forms import INPUT_CLASSES

from .models import LectureSession


class LectureSessionForm(forms.ModelForm):
    class Meta:
        model = LectureSession
        fields = ['date', 'start_time', 'end_time', 'topic_covered']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASSES}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': INPUT_CLASSES}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': INPUT_CLASSES}),
            'topic_covered': forms.TextInput(attrs={'class': INPUT_CLASSES}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            now = datetime.datetime.now()
            self.fields['date'].initial = now.date()
            self.fields['start_time'].initial = now.time().replace(second=0, microsecond=0)
            self.fields['end_time'].initial = (now + datetime.timedelta(hours=1)).time().replace(second=0, microsecond=0)
