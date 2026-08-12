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
    """A challan is 'paid' once payments recorded directly against it (see
    record_challan_payment) cover its total - tracked independently of the
    underlying fee items' overall balances, since a single fee item can now
    be split across several installment challans issued over time."""
    if challan.is_cancelled:
        return 'cancelled'
    paid = sum((p.amount_paid for p in challan.payments.all()), Decimal('0'))
    if paid >= challan.total_amount:
        return 'paid'
    if challan.due_date < datetime.date.today():
        return 'overdue'
    return 'unpaid'


def generate_challan(student, semester, created_by, items, due_days=14):
    """Issues a challan covering exactly the fee items and amounts the
    caller selected - not automatically every outstanding item at its full
    balance, since students often pay in installments (e.g. one category
    now, another later, or part of a category's balance now).

    `items` is a list of (StudentFeeItem, Decimal amount) pairs. Each
    amount must be > 0 and no more than that item's current outstanding
    balance - the rest of that item's balance is left outstanding for a
    future challan.

    Returns (challan, created). If an existing, non-cancelled, still-unpaid
    challan for this student+semester already covers this *exact* set of
    items and amounts, it's reused instead of issuing a duplicate (guards
    against an accidental double form submission, not against issuing a
    second, different installment challan while an earlier one is unpaid -
    that's expected with installments).

    Returns (None, False) if `items` is empty after validation.
    """
    requested = {}
    for item, amount in items:
        if item.student_id != student.pk or item.semester_id != semester.pk:
            continue
        outstanding = get_fee_item_balance(item)['outstanding']
        if amount is None or amount <= 0 or amount > outstanding:
            continue
        requested[item.pk] = (item, amount)

    if not requested:
        return None, False

    existing = (
        Challan.objects.filter(student=student, semester=semester, is_cancelled=False)
        .order_by('-issue_date', '-pk')
    )
    for candidate in existing:
        if get_challan_status(candidate) != 'unpaid':
            continue
        existing_lines = {line.fee_item_id: line.amount for line in candidate.lines.all()}
        requested_lines = {pk: amount for pk, (_item, amount) in requested.items()}
        if existing_lines == requested_lines:
            return candidate, False

    total = sum((amount for _item, amount in requested.values()), Decimal('0'))
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
        [ChallanLine(challan=challan, fee_item=item, amount=amount) for item, amount in requested.values()]
    )
    return challan, True


def record_challan_payment(challan, payment_date, payment_method, received_by):
    """Marks a challan as paid: creates one Payment per ChallanLine (for
    that line's exact amount), linked back to this challan so its status
    reflects only what was actually requested on it - matching the
    real-world flow where a student pays the full challan amount at the
    bank in one transaction. Safe to call only while the challan isn't
    already paid/cancelled; returns the created Payment list, or [] otherwise."""
    if get_challan_status(challan) not in ('unpaid', 'overdue'):
        return []
    payments = [
        Payment(
            fee_item=line.fee_item,
            challan=challan,
            amount_paid=line.amount,
            payment_date=payment_date,
            payment_method=payment_method,
            received_by=received_by,
        )
        for line in challan.lines.all()
    ]
    return Payment.objects.bulk_create(payments)


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
