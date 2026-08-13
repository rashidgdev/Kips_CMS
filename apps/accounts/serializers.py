from rest_framework import serializers

from .models import Department, Roles, StaffProfile, StudentProfile, TeacherProfile, User


class PersonSerializer(serializers.ModelSerializer):
    """Powers the People directory API list - mirrors the columns shown in
    templates/accounts/people_directory.html (name, role, roll no./employee
    ID, department, email, active status)."""

    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    identifier = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'full_name', 'first_name', 'last_name', 'email', 'phone_number',
            'role', 'role_display', 'is_active', 'identifier', 'department', 'profile_id',
        ]

    def get_identifier(self, obj):
        if getattr(obj, 'student_profile', None):
            return obj.student_profile.roll_number
        if getattr(obj, 'teacher_profile', None):
            return obj.teacher_profile.employee_id
        if getattr(obj, 'staff_profile', None):
            return obj.staff_profile.employee_id
        return None

    def get_profile_id(self, obj):
        """The StudentProfile/TeacherProfile/StaffProfile pk (not obj.id, which is
        the User pk) - apps/accounts/api_views.py's student_update/teacher_update/
        staff_update all key off the profile's own pk, not the user's."""
        for attr in ('student_profile', 'teacher_profile', 'staff_profile'):
            profile = getattr(obj, attr, None)
            if profile:
                return profile.pk
        return None

    def get_department(self, obj):
        if getattr(obj, 'teacher_profile', None) and obj.teacher_profile.department_id:
            return obj.teacher_profile.department.name
        if getattr(obj, 'student_profile', None) and getattr(obj.student_profile, 'program', None) and obj.student_profile.program.department_id:
            return obj.student_profile.program.department.name
        return None


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
