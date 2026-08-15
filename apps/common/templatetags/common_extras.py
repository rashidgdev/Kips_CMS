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


@register.simple_tag(takes_context=True)
def paginate_url(context, page_number, page_param='page'):
    """Builds a `?<page_param>=<page_number>` link that preserves every
    other current query param (filters, search terms, a second table's own
    page number, etc.) instead of dropping them the way a plain
    `?page=N` link would. `page_param` lets two independently-paginated
    tables on the same page (e.g. finance student_detail's "Fee Items" and
    "Challans" tables) page independently without resetting each other."""
    params = context['request'].GET.copy()
    params[page_param] = page_number
    return '?' + params.urlencode()
