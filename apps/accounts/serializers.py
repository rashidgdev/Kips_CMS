from rest_framework import serializers

from .models import Department, Roles, User


class DepartmentSerializer(serializers.ModelSerializer):
    """Mirrors apps/accounts/forms.py::DepartmentForm exactly: `hod` is a
    writable, optional choice restricted to HOD-role users (same queryset
    and help text the form used); `hod_label` is a read-only human string
    for the list table, matching what `{{ obj|get_attr:'hod' }}` rendered
    before (Department.hod's __str__ via User.__str__)."""

    hod = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role=Roles.HOD),
        required=False,
        allow_null=True,
        help_text=(
            'Optional - leave blank for now. Create the department first, add the '
            'HOD as a teacher assigned to it, then come back and edit this '
            'department to set them as HOD.'
        ),
    )
    hod_label = serializers.StringRelatedField(source='hod', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'hod', 'hod_label']
