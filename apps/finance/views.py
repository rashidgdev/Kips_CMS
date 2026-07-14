import csv
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy

from apps.accounts.models import Roles, StudentProfile
from apps.common.crud import CrudCreateView, CrudDeleteView, CrudListView, CrudUpdateView
from apps.common.exports import export_excel as export_excel_helper
from apps.common.exports import export_pdf as export_pdf_helper
from apps.common.middleware import get_profile
from apps.common.permissions import role_required

from .challan_pdf import render_challan_pdf
from .forms import FeeCategoryForm, FeeStructureForm, PaymentForm
from .models import Challan, FeeCategory, FeeStructure, StudentFeeItem
from .services import (
    generate_challan,
    generate_fee_items_for_semester,
    get_all_students_fee_summary,
    get_challan_status,
    get_fee_item_balance,
    get_student_fee_overview,
)

FINANCE_STAFF_ROLES = (Roles.ACCOUNTANT, Roles.ADMIN)


# --- Fee setup (categories & structures) ------------------------------------

class FeeCategoryListView(CrudListView):
    model = FeeCategory
    allowed_roles = FINANCE_STAFF_ROLES
    page_title = 'Fee Categories'
    list_display = [('name', 'Name')]
    add_url_name = 'finance:category-new'
    edit_url_name = 'finance:category-edit'
    delete_url_name = 'finance:category-delete'


class FeeCategoryCreateView(CrudCreateView):
    model = FeeCategory
    form_class = FeeCategoryForm
    allowed_roles = FINANCE_STAFF_ROLES
    page_title = 'Add Fee Category'
    success_url = reverse_lazy('finance:categories')
    success_message = 'Fee category created.'


class FeeCategoryUpdateView(CrudUpdateView):
    model = FeeCategory
    form_class = FeeCategoryForm
    allowed_roles = FINANCE_STAFF_ROLES
    page_title = 'Edit Fee Category'
    success_url = reverse_lazy('finance:categories')
    success_message = 'Fee category updated.'


class FeeCategoryDeleteView(CrudDeleteView):
    model = FeeCategory
    allowed_roles = FINANCE_STAFF_ROLES
    success_url = reverse_lazy('finance:categories')
    success_message = 'Fee category deleted.'


class FeeStructureListView(CrudListView):
    model = FeeStructure
    allowed_roles = FINANCE_STAFF_ROLES
    page_title = 'Fee Structures'
    list_display = [
        ('program', 'Program'), ('category', 'Category'),
        ('amount', 'Amount'), ('is_recurring', 'Recurring'),
    ]
    add_url_name = 'finance:structure-new'
    edit_url_name = 'finance:structure-edit'
    delete_url_name = 'finance:structure-delete'

    def get_queryset(self):
        return super().get_queryset().select_related('program', 'category')


class FeeStructureCreateView(CrudCreateView):
    model = FeeStructure
    form_class = FeeStructureForm
    allowed_roles = FINANCE_STAFF_ROLES
    page_title = 'Add Fee Structure'
    success_url = reverse_lazy('finance:structures')
    success_message = 'Fee structure created.'


class FeeStructureUpdateView(CrudUpdateView):
    model = FeeStructure
    form_class = FeeStructureForm
    allowed_roles = FINANCE_STAFF_ROLES
    page_title = 'Edit Fee Structure'
    success_url = reverse_lazy('finance:structures')
    success_message = 'Fee structure updated.'


class FeeStructureDeleteView(CrudDeleteView):
    model = FeeStructure
    allowed_roles = FINANCE_STAFF_ROLES
    success_url = reverse_lazy('finance:structures')
    success_message = 'Fee structure deleted.'


@role_required(Roles.ACCOUNTANT, Roles.ADMIN)
def student_list(request):
    summary = get_all_students_fee_summary()
    export_urls = {
        'csv': reverse('finance:export'),
        'excel': reverse('finance:export-excel'),
        'pdf': reverse('finance:export-pdf'),
    }
    return render(request, 'finance/student_list.html', {'summary': summary, 'export_urls': export_urls})


@role_required(Roles.ACCOUNTANT, Roles.ADMIN)
def student_detail(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)
    overview = get_student_fee_overview(student)
    challans = [
        {'challan': c, 'status': get_challan_status(c)}
        for c in student.challans.select_related('semester').order_by('-issue_date')
    ]
    return render(
        request,
        'finance/student_detail.html',
        {'student': student, 'overview': overview, 'challans': challans},
    )


@role_required(Roles.ACCOUNTANT, Roles.ADMIN)
def generate_items(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)
    if request.method == 'POST':
        if not student.current_semester:
            messages.error(request, f'{student} has no current semester set - cannot generate fee items.')
        else:
            created = generate_fee_items_for_semester(student, student.current_semester)
            if created:
                messages.success(request, f'Generated {len(created)} fee item(s) for {student.current_semester}.')
            else:
                messages.success(request, 'Fee items already up to date - nothing new to generate.')
    return redirect('finance:student-detail', student_id=student.pk)


@role_required(Roles.ACCOUNTANT, Roles.ADMIN)
def record_payment(request, item_id):
    fee_item = get_object_or_404(StudentFeeItem, pk=item_id)
    balance = get_fee_item_balance(fee_item)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['amount_paid'] > balance['outstanding']:
                form.add_error(
                    'amount_paid', f"Cannot exceed the outstanding balance of {balance['outstanding']}."
                )
            else:
                payment = form.save(commit=False)
                payment.fee_item = fee_item
                payment.received_by = request.user
                payment.save()
                messages.success(request, 'Payment recorded.')
                return redirect('finance:student-detail', student_id=fee_item.student_id)
    else:
        form = PaymentForm()

    return render(
        request,
        'finance/payment_form.html',
        {'fee_item': fee_item, 'balance': balance, 'form': form},
    )


_FEE_SUMMARY_HEADERS = ['Roll No.', 'Student', 'Program', 'Total Due', 'Total Paid', 'Outstanding']


def _fee_summary_export_rows(summary):
    return [
        [
            row['student'].roll_number,
            row['student'].user.get_full_name(),
            row['student'].program.code,
            row['total_due'],
            row['total_paid'],
            row['total_outstanding'],
        ]
        for row in summary
    ]


@role_required(Roles.ACCOUNTANT, Roles.ADMIN)
def export_csv(request):
    summary = get_all_students_fee_summary()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="fee_summary_{datetime.date.today()}.csv"'
    writer = csv.writer(response)
    writer.writerow(_FEE_SUMMARY_HEADERS)
    writer.writerows(_fee_summary_export_rows(summary))
    return response


@role_required(Roles.ACCOUNTANT, Roles.ADMIN)
def export_excel(request):
    summary = get_all_students_fee_summary()
    return export_excel_helper(
        f'fee_summary_{datetime.date.today()}', _FEE_SUMMARY_HEADERS, _fee_summary_export_rows(summary)
    )


@role_required(Roles.ACCOUNTANT, Roles.ADMIN)
def export_pdf(request):
    summary = get_all_students_fee_summary()
    return export_pdf_helper(
        f'fee_summary_{datetime.date.today()}',
        'Student Fee Summary',
        _FEE_SUMMARY_HEADERS,
        _fee_summary_export_rows(summary),
    )


@role_required(Roles.STUDENT)
def student_overview(request):
    profile = get_profile(request)
    overview = get_student_fee_overview(profile)
    challans = [
        {'challan': c, 'status': get_challan_status(c)}
        for c in profile.challans.select_related('semester').filter(is_cancelled=False)
    ]
    return render(
        request, 'finance/student_overview.html', {'overview': overview, 'challans': challans}
    )


# --- Challans ------------------------------------------------------------

@role_required(Roles.ACCOUNTANT, Roles.ADMIN)
def challan_generate(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)
    if request.method == 'POST':
        if not student.current_semester:
            messages.error(request, f'{student} has no current semester set - cannot issue a challan.')
        else:
            challan, created = generate_challan(student, student.current_semester, created_by=request.user)
            if challan and created:
                messages.success(request, f'Challan {challan.challan_number} issued for Rs. {challan.total_amount}.')
                return redirect('finance:challan-detail', challan_id=challan.pk)
            elif challan:
                messages.info(
                    request,
                    f'Challan {challan.challan_number} for Rs. {challan.total_amount} is already active and unpaid '
                    '- reused instead of issuing a duplicate. Cancel it first if you need a fresh one.',
                )
                return redirect('finance:challan-detail', challan_id=challan.pk)
            else:
                messages.info(request, 'Nothing outstanding for the current semester - no challan issued.')
    return redirect('finance:student-detail', student_id=student.pk)


@role_required(Roles.ACCOUNTANT, Roles.ADMIN)
def challan_list(request):
    challans = Challan.objects.select_related('student__user', 'semester').all()
    rows = [{'challan': c, 'status': get_challan_status(c)} for c in challans]
    return render(request, 'finance/challan_list.html', {'rows': rows})


@role_required(Roles.ACCOUNTANT, Roles.ADMIN)
def challan_detail(request, challan_id):
    challan = get_object_or_404(
        Challan.objects.select_related('student__user', 'semester'), pk=challan_id
    )
    lines = challan.lines.select_related('fee_item__category')
    status = get_challan_status(challan)
    return render(
        request, 'finance/challan_detail.html', {'challan': challan, 'lines': lines, 'status': status}
    )


@role_required(Roles.ACCOUNTANT, Roles.ADMIN)
def challan_cancel(request, challan_id):
    challan = get_object_or_404(Challan, pk=challan_id)
    if request.method == 'POST':
        challan.is_cancelled = True
        challan.save(update_fields=['is_cancelled'])
        messages.success(request, f'Challan {challan.challan_number} cancelled.')
    return redirect('finance:challan-detail', challan_id=challan.pk)


@login_required
def challan_pdf(request, challan_id):
    challan = get_object_or_404(Challan.objects.select_related('student__user'), pk=challan_id)
    profile = get_profile(request)
    is_owner = request.user.role == Roles.STUDENT and profile is not None and challan.student_id == profile.pk
    is_finance_staff = request.user.is_superuser or request.user.role in (Roles.ACCOUNTANT, Roles.ADMIN)
    if not (is_owner or is_finance_staff):
        raise PermissionDenied
    return render_challan_pdf(challan)
