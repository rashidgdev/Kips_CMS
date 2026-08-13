import datetime
from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.accounts.models import Roles, StudentProfile
from apps.common.api_generic import RoleScopedModelViewSet
from apps.common.api_permissions import HasRole, resolve_profile

from .forms import PaymentForm
from .models import Challan, FeeCategory, FeeStructure, Payment, StudentFeeItem
from .serializers import (
    ChallanLineSerializer,
    ChallanSerializer,
    FeeCategorySerializer,
    FeeStructureSerializer,
    PaymentSerializer,
    StudentFeeItemSerializer,
)
from .services import (
    generate_challan,
    generate_fee_items_for_semester,
    get_all_students_fee_summary,
    get_challan_status,
    get_fee_item_balance,
    get_student_fee_overview,
    record_challan_payment,
)

FINANCE_STAFF_ROLES = (Roles.ACCOUNTANT, Roles.ADMIN)


class FeeCategoryViewSet(RoleScopedModelViewSet):
    queryset = FeeCategory.objects.all()
    serializer_class = FeeCategorySerializer
    allowed_roles = FINANCE_STAFF_ROLES


class FeeStructureViewSet(RoleScopedModelViewSet):
    queryset = FeeStructure.objects.select_related('program', 'category')
    serializer_class = FeeStructureSerializer
    allowed_roles = FINANCE_STAFF_ROLES


def _serialize_overview(overview):
    return {
        'rows': [
            {
                'item': StudentFeeItemSerializer(row['item']).data,
                'paid': row['paid'], 'outstanding': row['outstanding'], 'status': row['status'],
            }
            for row in overview['rows']
        ],
        'total_due': overview['total_due'],
        'total_paid': overview['total_paid'],
        'total_outstanding': overview['total_outstanding'],
    }


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*FINANCE_STAFF_ROLES)])
def students_fee_summary_api(request):
    summary = get_all_students_fee_summary()
    return Response([
        {
            'student_id': row['student'].pk, 'roll_number': row['student'].roll_number,
            'name': row['student'].user.get_full_name(), 'program': row['student'].program.code,
            'total_due': row['total_due'], 'total_paid': row['total_paid'],
            'total_outstanding': row['total_outstanding'],
        }
        for row in summary
    ])


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*FINANCE_STAFF_ROLES)])
def student_fee_detail_api(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)
    overview = get_student_fee_overview(student)
    challans = student.challans.select_related('semester').order_by('-issue_date')
    return Response({
        'student_id': student.pk, 'roll_number': student.roll_number,
        'overview': _serialize_overview(overview),
        'challans': ChallanSerializer(challans, many=True).data,
    })


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*FINANCE_STAFF_ROLES)])
def generate_items_api(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)
    if not student.current_semester:
        return Response(
            {'detail': f'{student} has no current semester set - cannot generate fee items.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    created = generate_fee_items_for_semester(student, student.current_semester)
    return Response({
        'created': StudentFeeItemSerializer(created, many=True).data,
        'created_count': len(created),
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*FINANCE_STAFF_ROLES)])
def record_payment_api(request, item_id):
    fee_item = get_object_or_404(StudentFeeItem, pk=item_id)
    balance = get_fee_item_balance(fee_item)

    form = PaymentForm(request.data)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    if form.cleaned_data['amount_paid'] > balance['outstanding']:
        return Response(
            {'amount_paid': [f"Cannot exceed the outstanding balance of {balance['outstanding']}."]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    payment = form.save(commit=False)
    payment.fee_item = fee_item
    payment.received_by = request.user
    payment.save()
    return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([HasRole.for_roles(Roles.STUDENT)])
def my_fee_overview_api(request):
    profile = resolve_profile(request.user)
    overview = get_student_fee_overview(profile)
    challans = profile.challans.select_related('semester').filter(is_cancelled=False)
    return Response({
        'overview': _serialize_overview(overview),
        'challans': ChallanSerializer(challans, many=True).data,
    })


def _resolve_challan(request, challan_id):
    """A student may only access their own challan; finance staff may access any -
    mirrors finance/views.py::challan_pdf's ownership check."""
    challan = get_object_or_404(Challan.objects.select_related('student__user', 'semester'), pk=challan_id)
    is_staff = request.user.is_superuser or request.user.role in FINANCE_STAFF_ROLES
    is_owner = (
        request.user.role == Roles.STUDENT
        and resolve_profile(request.user) is not None
        and challan.student_id == resolve_profile(request.user).pk
    )
    if not (is_staff or is_owner):
        raise PermissionDenied('You do not have permission to access this challan.')
    return challan


@api_view(['GET', 'POST'])
@permission_classes([HasRole.for_roles(*FINANCE_STAFF_ROLES)])
def challan_generate_api(request, student_id):
    student = get_object_or_404(StudentProfile, pk=student_id)
    semester = student.current_semester
    if not semester:
        return Response(
            {'detail': f'{student} has no current semester set - cannot issue a challan.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    outstanding_rows = [
        row for row in get_student_fee_overview(student)['rows']
        if row['item'].semester_id == semester.pk and row['outstanding'] > 0
    ]

    if request.method == 'POST':
        selected = request.data.get('items', [])
        by_pk = {row['item'].pk: row['item'] for row in outstanding_rows}
        items = []
        for entry in selected:
            item = by_pk.get(int(entry.get('fee_item_id', 0)))
            if item is None:
                continue
            try:
                amount = Decimal(str(entry.get('amount')))
            except (InvalidOperation, TypeError):
                amount = None
            items.append((item, amount))

        if not items:
            return Response(
                {'detail': 'Select at least one fee item to include in the challan.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        challan, created = generate_challan(student, semester, created_by=request.user, items=items)
        if not challan:
            return Response(
                {'detail': 'Could not issue a challan - check that each amount is greater than zero and does '
                            'not exceed what is outstanding for that item.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {'challan': ChallanSerializer(challan).data, 'reused_existing': not created},
            status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED,
        )

    return Response({
        'student_id': student.pk, 'semester': str(semester),
        'outstanding_items': [
            {'fee_item': StudentFeeItemSerializer(row['item']).data, 'outstanding': row['outstanding']}
            for row in outstanding_rows
        ],
    })


@api_view(['GET'])
@permission_classes([HasRole.for_roles(*FINANCE_STAFF_ROLES)])
def challan_list_api(request):
    challans = Challan.objects.select_related('student__user', 'semester').all()
    return Response(ChallanSerializer(challans, many=True).data)


@api_view(['GET'])
@permission_classes([HasRole.for_roles(Roles.STUDENT, *FINANCE_STAFF_ROLES)])
def challan_detail_api(request, challan_id):
    challan = _resolve_challan(request, challan_id)
    lines = challan.lines.select_related('fee_item__category')
    return Response({
        'challan': ChallanSerializer(challan).data,
        'lines': ChallanLineSerializer(lines, many=True).data,
        'pdf_url': f'/finance/challans/{challan.pk}/pdf/',
    })


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*FINANCE_STAFF_ROLES)])
def challan_record_payment_api(request, challan_id):
    challan = get_object_or_404(Challan, pk=challan_id)
    raw_date = request.data.get('payment_date', '')
    try:
        payment_date = datetime.datetime.strptime(raw_date, '%Y-%m-%d').date()
    except ValueError:
        payment_date = datetime.date.today()
    payment_method = request.data.get('payment_method') or Payment.Method.CASH

    payments = record_challan_payment(
        challan, payment_date=payment_date, payment_method=payment_method, received_by=request.user
    )
    if not payments:
        return Response(
            {'detail': 'Could not record a payment - this challan may already be paid or cancelled.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return Response({'payments': PaymentSerializer(payments, many=True).data})


@api_view(['POST'])
@permission_classes([HasRole.for_roles(*FINANCE_STAFF_ROLES)])
def challan_cancel_api(request, challan_id):
    challan = get_object_or_404(Challan, pk=challan_id)
    challan.is_cancelled = True
    challan.save(update_fields=['is_cancelled'])
    return Response(ChallanSerializer(challan).data)
