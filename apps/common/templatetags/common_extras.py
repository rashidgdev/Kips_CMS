from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr_path):
    """Resolves a dotted attribute path (e.g. 'course_offering.course.code')
    at render time, calling it if the final value is a method - lets
    `generic_list.html` render arbitrary columns from a `list_display`
    config without a per-model template."""
    value = obj
    for part in attr_path.split('.'):
        if value is None:
            return ''
        value = getattr(value, part, '')
        if callable(value):
            value = value()
    return value
