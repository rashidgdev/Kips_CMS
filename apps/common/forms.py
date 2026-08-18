from django import forms

# Semantic Tailwind component classes defined in theme/static_src/src/styles.css
# (@layer components) - keeps every form's widget styling in one place instead
# of each app repeating its own long utility-class string.
INPUT_CLASSES = 'input-field'
CHECKBOX_CLASSES = 'checkbox-field'


class TailwindFormMixin:
    """Applies consistent Tailwind classes to every field's widget so
    per-model forms don't need to hand-declare a widgets={} dict for
    every field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', CHECKBOX_CLASSES)
            elif isinstance(widget, forms.DateInput):
                widget.attrs.setdefault('class', INPUT_CLASSES)
                # Widgets read their rendered `type` from `self.input_type`
                # (set once at construction), not from `attrs['type']` - a
                # `setdefault` on `attrs` alone just adds a *second*, ignored
                # `type` attribute to the tag instead of actually changing it.
                widget.input_type = 'date'
            elif isinstance(widget, forms.TimeInput):
                widget.attrs.setdefault('class', INPUT_CLASSES)
                widget.input_type = 'time'
            elif isinstance(widget, forms.DateTimeInput):
                widget.attrs.setdefault('class', INPUT_CLASSES)
                widget.input_type = 'datetime-local'
            else:
                widget.attrs.setdefault('class', INPUT_CLASSES)
