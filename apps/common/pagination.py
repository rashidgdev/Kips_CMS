"""
Shared server-side pagination for the read-only table views scattered
across every app (people directory, fee/challan lists, reports, rosters,
etc.) that don't go through apps/common/crud.py::CrudListView.
"""
from django.core.paginator import Paginator


def paginate_queryset(request, queryset, per_page=50, page_param='page'):
    """Returns a Django `Page` for `queryset` (a queryset OR a plain list -
    Paginator only needs len() + slicing) sliced to the page named by
    `?<page_param>=`. Uses `get_page()` rather than `page()` so a garbage
    or out-of-range page number clamps to the nearest valid page instead of
    raising a 404."""
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get(page_param))
