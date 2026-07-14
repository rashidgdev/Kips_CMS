from django import forms

from apps.common.forms import INPUT_CLASSES, TailwindFormMixin

from .models import Assessment, AssessmentCategory


class AssessmentCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = AssessmentCategory
        fields = ['name', 'default_weight_percent']


class AssessmentForm(forms.ModelForm):
    class Meta:
        model = Assessment
        fields = ['category', 'title', 'total_marks', 'weight_percent', 'date']
        widgets = {
            'category': forms.Select(attrs={'class': INPUT_CLASSES}),
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'total_marks': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'step': '0.5', 'min': '0'}),
            'weight_percent': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'step': '0.5', 'min': '0'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASSES}),
        }
