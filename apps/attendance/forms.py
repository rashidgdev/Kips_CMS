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
