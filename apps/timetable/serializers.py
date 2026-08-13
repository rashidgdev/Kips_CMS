from rest_framework import serializers

from .models import Room, TimeSlot, TimetableEntry


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'building', 'capacity', 'room_type']


class TimeSlotSerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    start_time_display = serializers.CharField(read_only=True)
    end_time_display = serializers.CharField(read_only=True)

    class Meta:
        model = TimeSlot
        fields = [
            'id', 'day_of_week', 'day_of_week_display', 'start_time', 'start_time_display',
            'end_time', 'end_time_display', 'label',
        ]


class TimetableEntrySerializer(serializers.ModelSerializer):
    course = serializers.StringRelatedField(source='course_offering.course', read_only=True)
    teacher = serializers.StringRelatedField(source='course_offering.teacher', read_only=True)
    room_name = serializers.StringRelatedField(source='room', read_only=True)
    time_slot_label = serializers.StringRelatedField(source='time_slot', read_only=True)

    class Meta:
        model = TimetableEntry
        fields = [
            'id', 'course_offering', 'course', 'teacher', 'room', 'room_name',
            'time_slot', 'time_slot_label',
        ]
