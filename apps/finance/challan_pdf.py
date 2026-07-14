"""
Renders a fee challan as a 3-copy (Bank / College / Student) printable PDF -
the standard payment-voucher format used by Pakistani educational
institutions, where a student takes the Bank Copy to the bank, the college
keeps its copy for record, and the student retains the third as proof.
"""
import io
import os

from django.conf import settings
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

LOGO_PATH = os.path.join(settings.BASE_DIR, 'static', 'images', 'kips-logo-icon.png')

PAGE_W, PAGE_H = A4
SECTION_H = PAGE_H / 3
COPY_LABELS = ['BANK COPY', 'COLLEGE COPY', 'STUDENT COPY']


def _draw_section(c, top_y, label, challan, lines):
    """Draws one copy of the challan with its top edge at `top_y`."""
    left = 12 * mm
    right = PAGE_W - 12 * mm
    width = right - left

    # Section border
    c.setStrokeColor(colors.HexColor('#9CA3AF'))
    c.setLineWidth(0.75)
    c.rect(left, top_y - SECTION_H + 4 * mm, width, SECTION_H - 8 * mm, stroke=1, fill=0)

    y = top_y - 10 * mm

    # Header: logo + institution name (left), copy label (right)
    if os.path.exists(LOGO_PATH):
        try:
            c.drawImage(LOGO_PATH, left + 4 * mm, y - 10 * mm, width=12 * mm, height=12 * mm,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    c.setFont('Helvetica-Bold', 13)
    c.setFillColor(colors.HexColor('#1E3A8A'))
    c.drawString(left + 20 * mm, y - 3 * mm, 'KIPS College Kasur Campus')
    c.setFont('Helvetica', 8.5)
    c.setFillColor(colors.HexColor('#4B5563'))
    c.drawString(left + 20 * mm, y - 8 * mm, 'Fee Payment Challan')

    c.setFont('Helvetica-Bold', 10)
    c.setFillColor(colors.HexColor('#1E3A8A'))
    c.drawRightString(right - 2 * mm, y - 3 * mm, label)

    y -= 16 * mm
    c.setStrokeColor(colors.HexColor('#D1D5DB'))
    c.line(left + 2 * mm, y, right - 2 * mm, y)
    y -= 6 * mm

    # Challan meta + student details, two columns
    c.setFont('Helvetica', 9)
    c.setFillColor(colors.black)
    col1_label_x = left + 4 * mm
    col1_val_x = left + 32 * mm
    col2_label_x = left + width / 2
    col2_val_x = col2_label_x + 26 * mm

    def field(x_label, x_val, y, label_text, value_text):
        c.setFont('Helvetica', 8.5)
        c.setFillColor(colors.HexColor('#6B7280'))
        c.drawString(x_label, y, label_text)
        c.setFont('Helvetica-Bold', 9.5)
        c.setFillColor(colors.black)
        c.drawString(x_val, y, str(value_text))

    field(col1_label_x, col1_val_x, y, 'Challan No.', challan.challan_number)
    field(col2_label_x, col2_val_x, y, 'Issue Date', challan.issue_date.strftime('%d-%b-%Y'))
    y -= 5.5 * mm
    field(col1_label_x, col1_val_x, y, 'Student', challan.student.user.get_full_name())
    field(col2_label_x, col2_val_x, y, 'Due Date', challan.due_date.strftime('%d-%b-%Y'))
    y -= 5.5 * mm
    field(col1_label_x, col1_val_x, y, 'Roll No.', challan.student.roll_number)
    field(col2_label_x, col2_val_x, y, 'Program', challan.student.program.code)
    y -= 5.5 * mm
    field(col1_label_x, col1_val_x, y, 'Semester', str(challan.semester))

    y -= 8 * mm

    # Fee items table
    table_left = left + 4 * mm
    table_right = right - 4 * mm
    table_w = table_right - table_left
    amount_col_w = 32 * mm
    desc_col_w = table_w - amount_col_w

    c.setFillColor(colors.HexColor('#EEF2FF'))
    c.rect(table_left, y - 5 * mm, table_w, 5 * mm, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 8.5)
    c.setFillColor(colors.HexColor('#1E3A8A'))
    c.drawString(table_left + 2 * mm, y - 3.7 * mm, 'Fee Category')
    c.drawRightString(table_right - 2 * mm, y - 3.7 * mm, 'Amount (Rs.)')
    y -= 5 * mm

    c.setFont('Helvetica', 9)
    c.setFillColor(colors.black)
    for line in lines:
        y -= 5 * mm
        c.drawString(table_left + 2 * mm, y + 1 * mm, str(line.fee_item.category))
        c.drawRightString(table_right - 2 * mm, y + 1 * mm, f'{line.amount:,.2f}')

    y -= 2 * mm
    c.setStrokeColor(colors.HexColor('#D1D5DB'))
    c.line(table_left, y, table_right, y)
    y -= 5.5 * mm
    c.setFont('Helvetica-Bold', 10)
    c.drawString(table_left + 2 * mm, y, 'Total Payable')
    c.drawRightString(table_right - 2 * mm, y, f'Rs. {challan.total_amount:,.2f}')

    # Signature lines
    sig_y = top_y - SECTION_H + 10 * mm
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#6B7280'))
    c.line(left + 4 * mm, sig_y + 4 * mm, left + 44 * mm, sig_y + 4 * mm)
    c.drawString(left + 4 * mm, sig_y, 'Accountant Signature')
    c.line(right - 44 * mm, sig_y + 4 * mm, right - 4 * mm, sig_y + 4 * mm)
    c.drawString(right - 44 * mm, sig_y, 'Bank Stamp / Received By')


def render_challan_pdf(challan):
    lines = list(challan.lines.select_related('fee_item__category').order_by('fee_item__category__name'))

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle(f'Challan {challan.challan_number}')

    for i, label in enumerate(COPY_LABELS):
        top_y = PAGE_H - (i * SECTION_H)
        _draw_section(c, top_y, label, challan, lines)

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="challan_{challan.challan_number}.pdf"'
    return response
