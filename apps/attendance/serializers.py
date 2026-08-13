from rest_framework import serializers

from .models import AttendanceRecord, LectureSession


class LectureSessionSerializer(serializers.ModelSerializer):
    course_offering_label = serializers.StringRelatedField(source='course_offering', read_only=True)

    class Meta:
        model = LectureSession
        fields = ['id', 'course_offering', 'course_offering_label', 'date', 'start_time', 'end_time', 'topic_covered']
        read_only_fields = ['course_offering']


class AttendanceRosterRowSerializer(serializers.Serializer):
    """Not model-backed - one row per enrolled student for the mark-attendance
    screen, matching templates/attendance/mark_attendance.html's rows."""
    student_id = serializers.IntegerField()
    roll_number = serializers.CharField()
    name = serializers.CharField()
    status = serializers.ChoiceField(choices=AttendanceRecord.Status.choices)
