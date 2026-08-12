from apps.common.api_generic import RoleScopedModelViewSet

from .models import Department, Roles
from .serializers import DepartmentSerializer

# Matches views.py's STAFF_MANAGEMENT_ROLES - kept as a local tuple here too
# so this file stays readable without cross-importing views.py.
STAFF_MANAGEMENT_ROLES = (Roles.COORDINATOR, Roles.ADMIN)


class DepartmentViewSet(RoleScopedModelViewSet):
    queryset = Department.objects.select_related('hod')
    serializer_class = DepartmentSerializer
    allowed_roles = STAFF_MANAGEMENT_ROLES
