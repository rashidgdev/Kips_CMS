from rest_framework import serializers

from .models import Course, CourseOffering, Enrollment, Program, Semester


class ProgramSerializer(serializers.ModelSerializer):
    department_label = serializers.StringRelatedField(source='department', read_only=True)

    class Meta:
        model = Program
        fields = ['id', 'name', 'code', 'department', 'department_label', 'total_semesters', 'degree_level', 'is_active']


class SemesterSerializer(serializers.ModelSerializer):
    program_label = serializers.StringRelatedField(source='program', read_only=True)

    class Meta:
        model = Semester
        fields = [
            'id', 'program', 'program_label', 'number', 'name', 'academic_year',
            'start_date', 'end_date', 'is_current',
        ]


class CourseSerializer(serializers.ModelSerializer):
    program_label = serializers.StringRelatedField(source='program', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'program', 'program_label', 'code', 'title', 'credit_hours', 'sessions_per_week',
            'semester_number', 'course_type', 'is_active',
        ]


class CourseOfferingSerializer(serializers.ModelSerializer):
    """`assigned_by`/`assigned_at` are read-only - the view fills assigned_by
    from the logged-in user on create, mirroring
    CourseOfferingCreateView.form_valid() exactly."""

    course_label = serializers.StringRelatedField(source='course', read_only=True)
    semester_label = serializers.StringRelatedField(source='semester', read_only=True)
    teacher_label = serializers.StringRelatedField(source='teacher', read_only=True)
    assigned_by_label = serializers.StringRelatedField(source='assigned_by', read_only=True)

    class Meta:
        model = CourseOffering
        fields = [
            'id', 'course', 'course_label', 'semester', 'semester_label', 'teacher', 'teacher_label',
            'section', 'max_seats', 'is_active', 'assigned_by', 'assigned_by_label', 'assigned_at',
        ]
        read_only_fields = ['assigned_by', 'assigned_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    student_label = serializers.StringRelatedField(source='student', read_only=True)
    course_offering_label = serializers.StringRelatedField(source='course_offering', read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'student_label', 'course_offering', 'course_offering_label',
            'status', 'enrolled_at',
        ]
        read_only_fields = ['enrolled_at']
