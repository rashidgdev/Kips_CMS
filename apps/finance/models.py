from django.conf import settings
from django.db import models

from apps.academics.models import Program, Semester
from apps.common.models import TimeStampedModel


class FeeCategory(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Fee categories'

    def __str__(self):
        return self.name


class FeeStructure(TimeStampedModel):
    """The standard fee package for a program - e.g. Tuition Fee recurs every
    semester, University Registration Fee is charged once at admission."""

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='fee_structures')
    category = models.ForeignKey(FeeCategory, on_delete=models.PROTECT, related_name='fee_structures')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_recurring = models.BooleanField(
        default=True, help_text='Recurring: charged every semester. One-time: charged once, at admission.'
    )

    class Meta:
        ordering = ['program', 'category']
        unique_together = ('program', 'category')

    def __str__(self):
        return f'{self.program.code} - {self.category} - {self.amount}'


class StudentFeeItem(TimeStampedModel):
    student = models.ForeignKey(
        'accounts.StudentProfile', on_delete=models.CASCADE, related_name='fee_items'
    )
    category = models.ForeignKey(FeeCategory, on_delete=models.PROTECT, related_name='fee_items')
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name='fee_items')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()

    class Meta:
        ordering = ['-semester__number', 'category']
        unique_together = ('student', 'category', 'semester')

    def __str__(self):
        return f'{self.student.roll_number} - {self.category} - {self.semester}'


class Payment(TimeStampedModel):
    class Method(models.TextChoices):
        CASH = 'cash', 'Cash'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        CHEQUE = 'cheque', 'Cheque'
        ONLINE = 'online', 'Online'

    fee_item = models.ForeignKey(StudentFeeItem, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=Method.choices, default=Method.CASH)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+'
    )

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f'Receipt #{self.pk} - {self.fee_item.student.roll_number} - {self.amount_paid}'


class Challan(TimeStampedModel):
    """A printable bank payment voucher for a student's outstanding fee items
    in one semester. `challan_number` is frozen at creation and never
    changes, so a reprinted challan still matches what the student took to
    the bank. Amounts on its lines are snapshotted at issue time (see
    ChallanLine) so the printed total stays accurate even if fee items are
    edited afterwards."""

    challan_number = models.CharField(max_length=30, unique=True, blank=True)
    student = models.ForeignKey(
        'accounts.StudentProfile', on_delete=models.CASCADE, related_name='challans'
    )
    semester = models.ForeignKey(Semester, on_delete=models.PROTECT, related_name='challans')
    issue_date = models.DateField()
    due_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+'
    )
    is_cancelled = models.BooleanField(default=False)

    class Meta:
        ordering = ['-issue_date', '-pk']

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new and not self.challan_number:
            self.challan_number = f'KIPS-{self.issue_date.year}-{self.pk:06d}'
            super().save(update_fields=['challan_number'])

    def __str__(self):
        return self.challan_number


class ChallanLine(TimeStampedModel):
    """One fee item on a challan, with the outstanding amount frozen at the
    moment the challan was issued."""

    challan = models.ForeignKey(Challan, on_delete=models.CASCADE, related_name='lines')
    fee_item = models.ForeignKey(
        StudentFeeItem, on_delete=models.PROTECT, related_name='challan_lines'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('challan', 'fee_item')

    def __str__(self):
        return f'{self.challan.challan_number} - {self.fee_item.category}'
