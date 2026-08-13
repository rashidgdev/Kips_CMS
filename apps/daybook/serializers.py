from rest_framework import serializers

from .models import DayBookEntry, MonthlyWorkloadSnapshot


class DayBookEntrySerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField(source='session.course_offering.course', read_only=True)
    teacher = serializers.StringRelatedField(source='session.course_offering.teacher', read_only=True)
    session_date = serializers.DateField(source='session.date', read_only=True)
    topic_covered = serializers.CharField(source='session.topic_covered', read_only=True)
    verified_by_name = serializers.SerializerMethodField()
    is_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = DayBookEntry
        fields = [
            'id', 'session', 'course', 'teacher', 'session_date', 'topic_covered',
            'verified_by_name', 'verified_at', 'remarks', 'is_verified',
        ]

    def get_verified_by_name(self, obj):
        return obj.verified_by.get_full_name() if obj.verified_by else None


class MonthlyWorkloadSnapshotSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='teacher.employee_id', read_only=True)

    class Meta:
        model = MonthlyWorkloadSnapshot
        fields = [
            'id', 'teacher', 'teacher_name', 'employee_id', 'year', 'month',
            'total_lectures', 'verified_lectures', 'per_lecture_rate', 'total_amount',
        ]
