import csv
import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.models import Roles
from apps.common.exports import export_excel, export_pdf
from apps.common.middleware import get_profile
from apps.common.permissions import role_required

from .models import DayBookEntry, MonthlyWorkloadSnapshot
from .services import generate_workload_snapshots, get_all_teachers_workload, get_teacher_workload, verify_day_book_entry


@role_required(Roles.TEACHER, Roles.HOD)
def day_book_list(request):
    profile = get_profile(request)
    entries = DayBookEntry.objects.filter(session__course_offering__teacher=profile).select_related(
        'session__course_offering__course', 'verified_by'
    )
    today = datetime.date.today()
    workload = get_teacher_workload(profile, today.year, today.month)
    return render(
        request,
        'daybook/day_book_list.html',
        {
            'entries': entries,
            'workload': workload,
            'today': today,
            'pay_label': f'Estimated pay ({today:%b %Y})',
        },
    )


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def verify_queue(request):
    pending = DayBookEntry.objects.filter(verified_by__isnull=True).select_related(
        'session__course_offering__course', 'session__course_offering__teacher__user'
    )
    return render(request, 'daybook/verify_queue.html', {'pending': pending})


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def verify_entry(request, entry_id):
    if request.method == 'POST':
        entry = get_object_or_404(DayBookEntry, pk=entry_id)
        verify_day_book_entry(entry, verified_by=request.user, remarks=request.POST.get('remarks', ''))
        messages.success(request, 'Day book entry verified.')
    return redirect('daybook:verify-queue')


def _parse_year_month(request):
    today = datetime.date.today()
    value = request.GET.get('month')
    if value:
        try:
            year, month = (int(part) for part in value.split('-'))
            return year, month
        except (ValueError, TypeError):
            pass
    return today.year, today.month


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def workload_report(request):
    year, month = _parse_year_month(request)

    if request.method == 'POST':
        generate_workload_snapshots(year, month, generated_by=request.user)
        messages.success(request, f'Payroll snapshot generated for {year}-{month:02d}.')
        return redirect(f"{request.path}?month={year}-{month:02d}")

    rows = get_all_teachers_workload(year, month)
    total_amount = sum((row['total_amount'] for row in rows), start=0)
    snapshot_generated = MonthlyWorkloadSnapshot.objects.filter(year=year, month=month).exists()
    month_value = f'{year}-{month:02d}'

    return render(
        request,
        'daybook/workload_report.html',
        {
            'rows': rows,
            'year': year,
            'month': month,
            'month_value': month_value,
            'total_amount': total_amount,
            'snapshot_generated': snapshot_generated,
            'export_urls': {
                'csv': f"{reverse('daybook:workload-export')}?month={month_value}",
                'excel': f"{reverse('daybook:workload-export-excel')}?month={month_value}",
                'pdf': f"{reverse('daybook:workload-export-pdf')}?month={month_value}",
            },
        },
    )


_WORKLOAD_HEADERS = ['Employee ID', 'Teacher', 'Department', 'Total Lectures', 'Verified Lectures', 'Rate', 'Amount']


def _workload_export_rows(rows):
    return [
        [
            row['teacher'].employee_id,
            row['teacher'].user.get_full_name(),
            row['teacher'].department.code,
            row['total_lectures'],
            row['verified_lectures'],
            row['per_lecture_rate'],
            row['total_amount'],
        ]
        for row in rows
    ]


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def workload_report_csv(request):
    year, month = _parse_year_month(request)
    rows = get_all_teachers_workload(year, month)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="workload_{year}_{month:02d}.csv"'
    writer = csv.writer(response)
    writer.writerow(_WORKLOAD_HEADERS)
    writer.writerows(_workload_export_rows(rows))
    return response


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def workload_report_excel(request):
    year, month = _parse_year_month(request)
    rows = get_all_teachers_workload(year, month)
    return export_excel(f'workload_{year}_{month:02d}', _WORKLOAD_HEADERS, _workload_export_rows(rows))


@role_required(Roles.COORDINATOR, Roles.ADMIN)
def workload_report_pdf(request):
    year, month = _parse_year_month(request)
    rows = get_all_teachers_workload(year, month)
    return export_pdf(
        f'workload_{year}_{month:02d}',
        'Faculty Workload Report',
        _WORKLOAD_HEADERS,
        _workload_export_rows(rows),
        subtitle=f'{year}-{month:02d}',
    )
