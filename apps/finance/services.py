import datetime
from decimal import Decimal

from .models import Challan, ChallanLine, FeeStructure, Payment, StudentFeeItem


def generate_fee_items_for_semester(student, semester):
    """Idempotently creates this student's fee items for `semester` from their
    program's FeeStructure. Recurring items (tuition, exam fee) are created
    every semester; one-time items (registration fee) are only created if the
    student has never been charged that category before, in any semester."""
    created = []
    structures = FeeStructure.objects.filter(program=student.program).select_related('category')

    for structure in structures:
        if not structure.is_recurring:
            already_charged = StudentFeeItem.objects.filter(
                student=student, category=structure.category
            ).exists()
            if already_charged:
                continue

        item, was_created = StudentFeeItem.objects.get_or_create(
            student=student,
            category=structure.category,
            semester=semester,
            defaults={
                'amount_due': structure.amount,
                'due_date': semester.start_date + datetime.timedelta(days=14),
            },
        )
        if was_created:
            created.append(item)

    return created


def get_fee_item_balance(fee_item):
    paid = sum((p.amount_paid for p in fee_item.payments.all()), Decimal('0'))
    outstanding = fee_item.amount_due - paid
    if outstanding <= 0:
        status = 'paid'
    elif paid > 0:
        status = 'partial'
    elif fee_item.due_date < datetime.date.today():
        status = 'overdue'
    else:
        status = 'unpaid'
    return {'paid': paid, 'outstanding': outstanding, 'status': status}


def get_student_fee_overview(student):
    items = student.fee_items.select_related('category', 'semester').prefetch_related('payments')
    rows = []
    total_due = Decimal('0')
    total_paid = Decimal('0')
    for item in items:
        balance = get_fee_item_balance(item)
        total_due += item.amount_due
        total_paid += balance['paid']
        rows.append({'item': item, **balance})
    return {
        'rows': rows,
        'total_due': total_due,
        'total_paid': total_paid,
        'total_outstanding': total_due - total_paid,
    }


def get_challan_status(challan):
    """Computed on read, same pattern as fee item status - a challan is
    'paid' once every fee item it covers has been fully settled, however
    that happened (no separate payment-to-challan bookkeeping needed)."""
    if challan.is_cancelled:
        return 'cancelled'
    lines = challan.lines.select_related('fee_item').prefetch_related('fee_item__payments')
    if all(get_fee_item_balance(line.fee_item)['outstanding'] <= 0 for line in lines):
        return 'paid'
    return 'unpaid'


def generate_challan(student, semester, created_by, due_days=14):
    """Issues a challan covering every currently-outstanding fee item for this
    student in this semester.

    Returns (challan, created): `created` is False if an active, unpaid
    challan for this student+semester already exists - that challan is
    reused (same number, same amount) instead of issuing a duplicate live
    voucher for the same dues. To reissue with a fresh number (e.g. the
    student lost it), cancel the old one first.

    Returns (None, False) if nothing is outstanding - avoids issuing an
    empty/zero-amount voucher.
    """
    existing = (
        Challan.objects.filter(student=student, semester=semester, is_cancelled=False)
        .order_by('-issue_date', '-pk')
        .first()
    )
    if existing and get_challan_status(existing) == 'unpaid':
        return existing, False

    items = StudentFeeItem.objects.filter(student=student, semester=semester)
    lines_to_create = []
    total = Decimal('0')
    for item in items:
        balance = get_fee_item_balance(item)
        if balance['outstanding'] > 0:
            lines_to_create.append((item, balance['outstanding']))
            total += balance['outstanding']

    if not lines_to_create:
        return None, False

    today = datetime.date.today()
    challan = Challan.objects.create(
        student=student,
        semester=semester,
        issue_date=today,
        due_date=today + datetime.timedelta(days=due_days),
        total_amount=total,
        created_by=created_by,
    )
    ChallanLine.objects.bulk_create(
        [ChallanLine(challan=challan, fee_item=item, amount=amount) for item, amount in lines_to_create]
    )
    return challan, True


def get_all_students_fee_summary():
    from apps.accounts.models import StudentProfile

    students = StudentProfile.objects.select_related('user', 'program').order_by('roll_number')
    summary = []
    for student in students:
        overview = get_student_fee_overview(student)
        summary.append(
            {
                'student': student,
                'total_due': overview['total_due'],
                'total_paid': overview['total_paid'],
                'total_outstanding': overview['total_outstanding'],
            }
        )
    return summary
