from django.contrib import admin

from .models import Room, TimeSlot, TimetableEntry


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'start_time', 'end_time', 'label')
    list_filter = ('day_of_week',)
    search_fields = ('label',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'building', 'capacity', 'room_type')
    list_filter = ('room_type',)
    search_fields = ('name', 'building')


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ('course_offering', 'room', 'time_slot', 'created_by')
    list_filter = ('course_offering__semester', 'room')
    search_fields = ('course_offering__course__code',)
    autocomplete_fields = ('course_offering', 'room', 'time_slot', 'created_by')
