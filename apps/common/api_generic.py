"""
Generic DRF building blocks mirroring apps/common/crud.py's Django CRUD
base classes (CrudListView/CreateView/UpdateView/DeleteView), so simple
"setup/reference data" resources (Department, Program, Room, ...) get a
REST API with the same pagination/permission shape as their existing
template views, instead of each resource re-implementing it.
"""
from rest_framework import viewsets

from .api_metadata import StandardPagination
from .api_permissions import HasRole

# Re-exported for convenience so other apps only need one import line -
# actual definitions live in api_metadata.py (see that module's docstring
# for why: avoids a circular import with rest_framework.views).
__all__ = ['RoleScopedModelViewSet', 'StandardPagination']


class RoleScopedModelViewSet(viewsets.ModelViewSet):
    """A ModelViewSet gated exactly like apps/common/crud.py's
    RoleRequiredMixin-based views: superuser always allowed, else the
    user's role must be in `allowed_roles`. Provides list/retrieve/create/
    update/partial_update/destroy - the same five operations spread across
    CrudListView/CreateView/UpdateView/DeleteView today (retrieve doubles
    as the data source for the "confirm delete" screen).

    Subclasses set: queryset, serializer_class, allowed_roles.
    """
    allowed_roles = ()
    pagination_class = StandardPagination

    def get_permissions(self):
        return [HasRole.for_roles(*self.allowed_roles)()]
