import datetime

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.accounts.models import Roles
from apps.common.api_permissions import HasRole, resolve_profile

from .models import DayBookEntry, MonthlyWorkloadSnapshot
from .serializers import DayBookEntrySerializer, MonthlyWorkloadSnapshotSerializer
from .services import generate_workload_snapshots, get_all_teachers_workload, get_teacher_workload, verify_day_book_entry

STAFF_ROLES = (Roles.COORDINATOR, Roles.ADMIN)
TEACHER_ROLES = (Roles.TEACHER, Roles.HOD)


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*TEACHER_ROLES)])
def day_book_list_api(request):
    profile = resolve_profile(request.user)
    entries = DayBookEntry.objects.filter(session__course_offering__teacher=profile).select_related(
        'session__course_offering__course', 'verified_by'
    )
    today = datetime.date.today()
    workload = get_teacher_workload(profile, today.year, today.month)
    return Response({
        'entries': DayBookEntrySerializer(entries, many=True).data,
        'workload': {k: v for k, v in workload.items() if k != 'teacher'},
    })


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def verify_queue_api(request):
    pending = DayBookEntry.objects.filter(verified_by__isnull=True).select_related(
        'session__course_offering__course', 'session__course_offering__teacher__user'
    )
    return Response(DayBookEntrySerializer(pending, many=True).data)


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def verify_entry_api(request, entry_id):
    entry = get_object_or_404(DayBookEntry, pk=entry_id)
    verify_day_book_entry(entry, verified_by=request.user, remarks=request.data.get('remarks', ''))
    return Response(DayBookEntrySerializer(entry).data)


def _parse_year_month(request):
    today = datetime.date.today()
    value = request.query_params.get('month')
    if value:
        try:
            year, month = (int(part) for part in value.split('-'))
            return year, month
        except (ValueError, TypeError):
            pass
    return today.year, today.month


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def workload_report_api(request):
    year, month = _parse_year_month(request)
    rows = get_all_teachers_workload(year, month)
    total_amount = sum((row['total_amount'] for row in rows), start=0)
    snapshot_generated = MonthlyWorkloadSnapshot.objects.filter(year=year, month=month).exists()
    return Response({
        'year': year, 'month': month, 'total_amount': total_amount,
        'snapshot_generated': snapshot_generated,
        'rows': [
            {
                'teacher_id': row['teacher'].pk, 'employee_id': row['teacher'].employee_id,
                'teacher_name': row['teacher'].user.get_full_name(),
                'department': row['teacher'].department.code,
                'total_lectures': row['total_lectures'], 'verified_lectures': row['verified_lectures'],
                'unverified_lectures': row['unverified_lectures'],
                'per_lecture_rate': row['per_lecture_rate'], 'total_amount': row['total_amount'],
            }
            for row in rows
        ],
    })


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*STAFF_ROLES)])
def workload_snapshot_generate_api(request):
    year, month = _parse_year_month(request)
    rows = generate_workload_snapshots(year, month, generated_by=request.user)
    snapshots = MonthlyWorkloadSnapshot.objects.filter(year=year, month=month).select_related('teacher__user')
    return Response({
        'year': year, 'month': month, 'generated_count': len(rows),
        'snapshots': MonthlyWorkloadSnapshotSerializer(snapshots, many=True).data,
    }, status=status.HTTP_201_CREATED)
