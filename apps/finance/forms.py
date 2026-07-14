import datetime

from django import forms

from apps.common.forms import INPUT_CLASSES, TailwindFormMixin

from .models import FeeCategory, FeeStructure, Payment


class FeeCategoryForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = FeeCategory
        fields = ['name']


class FeeStructureForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['program', 'category', 'amount', 'is_recurring']


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_date', 'payment_method']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'step': '0.01', 'min': '0.01'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': INPUT_CLASSES}),
            'payment_method': forms.Select(attrs={'class': INPUT_CLASSES}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            self.fields['payment_date'].initial = datetime.date.today()
