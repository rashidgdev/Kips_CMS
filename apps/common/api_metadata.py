"""
Classes referenced by name from REST_FRAMEWORK settings (DEFAULT_PAGINATION_CLASS,
DEFAULT_METADATA_CLASS). Kept in their own module, deliberately NOT importing
`rest_framework.viewsets`/`views`: those modules read `api_settings.DEFAULT_METADATA_CLASS`
at class-definition time (as an APIView class attribute), so importing them
from a module referenced by that same setting creates a circular import.
apps/common/api_generic.py (which does need `viewsets`) imports from here,
never the other way around.
"""
from django.urls import reverse
from rest_framework.metadata import SimpleMetadata
from rest_framework.pagination import PageNumberPagination
from rest_framework.relations import RelatedField

_ID_PLACEHOLDER_PK = 999999999


def id_template_url(url_name, placeholder='{id}'):
    """Reverses a `<pk>`-based URL once and swaps the placeholder pk back out
    for a JS-friendly token, e.g. '/accounts/departments/{id}/edit/' - lets
    the JS-shell templates build per-row edit/delete links without
    duplicating urls.py's URL structure in JS."""
    return reverse(url_name, args=[_ID_PLACEHOLDER_PK]).replace(str(_ID_PLACEHOLDER_PK), placeholder)


class StandardPagination(PageNumberPagination):
    """Matches apps/common/crud.py CrudListView.paginate_by = 50."""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class ChoiceMetadata(SimpleMetadata):
    """Extends DRF's default OPTIONS response to include {value,display_name}
    choice lists for writable ForeignKey fields too - DRF only does this for
    ChoiceField out of the box. The generic JS form renderer
    (static/js/core/crud.js) calls OPTIONS on a resource before rendering its
    create/edit form and uses this to build <select> dropdowns for FK fields
    (e.g. Department.hod) without each resource needing a bespoke "choices"
    endpoint - set as REST_FRAMEWORK.DEFAULT_METADATA_CLASS, so every
    resource gets this automatically."""

    def get_field_info(self, field):
        info = super().get_field_info(field)
        if isinstance(field, RelatedField) and not field.read_only:
            queryset = getattr(field, 'queryset', None)
            if queryset is not None:
                info['choices'] = [
                    {'value': obj.pk, 'display_name': str(obj)} for obj in queryset.all()[:500]
                ]
        return info
