from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from apps.academics.models import CourseOffering, Enrollment, Semester
from apps.accounts.models import Roles
from apps.common.api_generic import RoleScopedModelViewSet
from apps.common.api_permissions import HasRole, resolve_profile

from .forms import TimeSlotGeneratorForm, TimeSlotResizeForm, TimetableEntryForm
from .models import Room, TimeSlot, TimetableEntry
from .serializers import RoomSerializer, TimeSlotSerializer, TimetableEntrySerializer
from .services import auto_schedule_semester, build_grid, check_conflicts, generate_time_slots, resize_day_slots

STAFF_ROLES = (Roles.COORDINATOR, Roles.ADMIN)
TEACHER_ROLES = (Roles.TEACHER, Roles.HOD)


class RoomViewSet(RoleScopedModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    allowed_roles = STAFF_ROLES


class TimeSlotViewSet(RoleScopedModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    allowed_roles = STAFF_ROLES

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        pks = request.data.get('ids', [])
        deleted, blocked = [], []
        for slot in TimeSlot.objects.filter(pk__in=pks):
            try:
                slot.delete()
                deleted.append(int(slot.pk))
            except ProtectedError:
                blocked.append({'id': slot.pk, 'label': str(slot)})
        return Response({'deleted': deleted, 'blocked': blocked})

    @action(detail=True, methods=['post'], url_path='resize')
    def resize(self, request, pk=None):
        slot = self.get_object()
        form = TimeSlotResizeForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        new_slots, remapped_count = resize_day_slots(
            slot.day_of_week, form.cleaned_data['lecture_duration_minutes']
        )
        return Response({
            'slots': TimeSlotSerializer(new_slots, many=True).data,
            'remapped_entry_count': remapped_count,
        })


def _get_semester(semester_id):
    if semester_id:
        return get_object_or_404(Semester, pk=semester_id)
    current = Semester.objects.filter(is_current=True).first()
    return current or Semester.objects.order_by('-start_date').first()


def _serialize_grid(grid):
    """JSON-friendly reshape of build_grid()'s output: period rows carry a
    list of {day, entry_id, course, teacher, room} cells instead of Django
    model instances, break rows pass through as-is."""
    rows = []
    for row in grid['rows']:
        if row['type'] == 'break':
            rows.append({
                'type': 'break', 'start_time': row['start_time'], 'end_time': row['end_time'],
                'duration_minutes': row['duration_minutes'],
            })
            continue
        cells = []
        for cell in row['cells']:
            entry = cell['entry']
            cells.append({
                'day': cell['day'],
                'day_label': cell['day_label'],
                'entry_id': entry.pk if entry else None,
                'course': str(entry.course_offering.course) if entry else None,
                'teacher': str(entry.course_offering.teacher) if entry else None,
                'room': str(entry.room) if entry else None,
            })
        rows.append({
            'type': 'period',
            'start_time': row['period']['start_time'], 'end_time': row['period']['end_time'],
            'label': row['period']['label'], 'cells': cells,
        })
    return {'days': [{'value': v, 'label': label} for v, label in grid['days']], 'rows': rows}


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def semester_grid_api(request, semester_id=None):
    semester = _get_semester(semester_id)
    grid = {'days': [], 'rows': []}
    if semester:
        entries = TimetableEntry.objects.filter(course_offering__semester=semester)
        grid = build_grid(entries)
    return Response({
        'semester': {'id': semester.pk, 'name': str(semester)} if semester else None,
        'grid': _serialize_grid(grid),
        'pdf_url': f'/timetable/semester/{semester.pk}/pdf/' if semester else None,
    })


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def semesters_list_api(request):
    semesters = Semester.objects.select_related('program').order_by('-is_current', 'program__name', '-number')
    return Response([
        {'id': s.pk, 'name': str(s), 'is_current': s.is_current} for s in semesters
    ])


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def schedule_entry_api(request, semester_id):
    semester = get_object_or_404(Semester, pk=semester_id)
    offerings = CourseOffering.objects.filter(semester=semester, is_active=True)

    form = TimetableEntryForm(request.data, course_offering_queryset=offerings)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    conflicts = check_conflicts(
        form.cleaned_data['course_offering'], form.cleaned_data['room'], form.cleaned_data['time_slot'],
    )
    if conflicts:
        return Response({'errors': conflicts}, status=status.HTTP_400_BAD_REQUEST)

    entry = form.save(commit=False)
    entry.created_by = request.user
    entry.save()
    return Response(TimetableEntrySerializer(entry).data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def unschedule_entry_api(request, entry_id):
    entry = get_object_or_404(TimetableEntry, pk=entry_id)
    entry.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def auto_schedule_semester_api(request, semester_id):
    semester = get_object_or_404(Semester, pk=semester_id)
    created, unscheduled = auto_schedule_semester(semester, created_by=request.user)
    return Response({
        'created': TimetableEntrySerializer(created, many=True).data,
        'unscheduled': [
            {'course_offering_id': offering.pk, 'course_offering': str(offering), 'reason': reason}
            for offering, reason in unscheduled
        ],
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def timeslot_generate_api(request):
    form = TimeSlotGeneratorForm(request.data)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    data = form.cleaned_data
    created, skipped = generate_time_slots(
        days=[int(d) for d in data['days']],
        day_start_time=data['day_start_time'],
        lecture_duration_minutes=data['lecture_duration_minutes'],
        number_of_lectures=data['number_of_lectures'],
        breaks=data['breaks'],
    )
    return Response({
        'created': TimeSlotSerializer(created, many=True).data,
        'skipped_count': len(skipped),
    }, status=status.HTTP_201_CREATED)


def _teacher_current_entries(profile):
    return TimetableEntry.objects.filter(
        course_offering__teacher=profile, course_offering__semester__is_current=True
    )


def _student_current_entries(profile):
    return TimetableEntry.objects.filter(
        course_offering__enrollments__student=profile,
        course_offering__enrollments__status=Enrollment.Status.ENROLLED,
    ).distinct()


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*TEACHER_ROLES)])
def teacher_timetable_api(request):
    profile = resolve_profile(request.user)
    grid = build_grid(_teacher_current_entries(profile))
    return Response({'grid': _serialize_grid(grid), 'pdf_url': '/timetable/mine/pdf/'})


@api_view(['GET'])
@permission_classes([HasRole.for_roles(Roles.STUDENT)])
def student_timetable_api(request):
    profile = resolve_profile(request.user)
    grid = build_grid(_student_current_entries(profile))
    return Response({'grid': _serialize_grid(grid), 'pdf_url': '/timetable/my/pdf/'})
