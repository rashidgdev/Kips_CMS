"""
Renders the actual day x period timetable grid as a PDF - the same shape
shown on screen (templates/timetable/_grid.html), including labeled break
rows - instead of the generic flat list-of-classes export every other
report uses (apps/common/exports.py::export_pdf). Column widths are
computed explicitly so the table fills the full landscape page instead of
reportlab's default "shrink to fit content" sizing.
"""
import io

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.common.exports import LETTERHEAD_TOP_MARGIN_MM, draw_pdf_letterhead

PAGE_SIZE = landscape(A4)
MARGIN = 10 * mm
TOP_MARGIN = LETTERHEAD_TOP_MARGIN_MM * mm
TIME_COL_WIDTH = 30 * mm

_styles = getSampleStyleSheet()
_header_style = ParagraphStyle('GridHeader', parent=_styles['Normal'], fontSize=8, textColor=colors.white, fontName='Helvetica-Bold')
_time_style = ParagraphStyle('GridTime', parent=_styles['Normal'], fontSize=7.5, textColor=colors.HexColor('#4B5563'), fontName='Helvetica-Bold', leading=9)
_entry_name_style = ParagraphStyle('GridEntryName', parent=_styles['Normal'], fontSize=7.5, textColor=colors.HexColor('#1E3A8A'), fontName='Helvetica-Bold', leading=9)
_entry_detail_style = ParagraphStyle('GridEntryDetail', parent=_styles['Normal'], fontSize=6.5, textColor=colors.HexColor('#374151'), leading=8)
_empty_style = ParagraphStyle('GridEmpty', parent=_styles['Normal'], fontSize=8, textColor=colors.HexColor('#D1D5DB'), alignment=1)
_break_style = ParagraphStyle('GridBreak', parent=_styles['Normal'], fontSize=8, textColor=colors.HexColor('#92400E'), fontName='Helvetica-Bold', alignment=1)


def _fmt12(value):
    return value.strftime('%I:%M %p').lstrip('0')


def _period_cell(entries):
    if not entries:
        return Paragraph('&ndash;', _empty_style)
    blocks = []
    show_section = len(entries) > 1
    for index, entry in enumerate(entries):
        if index > 0:
            blocks.append(Spacer(1, 3))
        if show_section:
            blocks.append(Paragraph(f'Section {entry.course_offering.section}', _entry_detail_style))
        blocks.extend([
            Paragraph(entry.course_offering.course.title, _entry_name_style),
            Paragraph(str(entry.room), _entry_detail_style),
            Paragraph(entry.course_offering.teacher.user.get_full_name(), _entry_detail_style),
        ])
    return blocks


def render_timetable_grid_pdf(grid, title, subtitle=''):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=PAGE_SIZE, title=title,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=TOP_MARGIN, bottomMargin=MARGIN,
    )

    def _letterhead(c, doc):
        draw_pdf_letterhead(c, doc.pagesize[0], doc.pagesize[1])

    elements = [Paragraph(title, _styles['Title'])]
    if subtitle:
        elements.append(Paragraph(subtitle, _styles['Normal']))
    elements.append(Spacer(1, 8))

    days = grid['days']
    available_width = PAGE_SIZE[0] - 2 * MARGIN
    day_col_width = (available_width - TIME_COL_WIDTH) / len(days) if days else available_width
    col_widths = [TIME_COL_WIDTH] + [day_col_width] * len(days)

    header = ['Time'] + [Paragraph(day_label, _header_style) for _day_value, day_label in days]
    data = [header]
    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]

    row_index = 1
    for row in grid['rows']:
        if row['type'] == 'break':
            label = f"BREAK &middot; {_fmt12(row['start_time'])}-{_fmt12(row['end_time'])} ({row['duration_minutes']} min)"
            data.append([Paragraph(label, _break_style)] + [''] * len(days))
            style_commands.append(('SPAN', (0, row_index), (-1, row_index)))
            style_commands.append(('BACKGROUND', (0, row_index), (-1, row_index), colors.HexColor('#FFFBEB')))
        else:
            time_label = Paragraph(f"{row['period']['label']}<br/>{_fmt12(row['period']['start_time'])}-{_fmt12(row['period']['end_time'])}", _time_style)
            cells = [time_label] + [_period_cell(cell['entries']) for cell in row['cells']]
            data.append(cells)
            style_commands.append(('BACKGROUND', (0, row_index), (0, row_index), colors.HexColor('#F9FAFB')))
        row_index += 1

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle(style_commands))
    elements.append(table)

    doc.build(elements, onFirstPage=_letterhead, onLaterPages=_letterhead)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{title.replace(" ", "_")}.pdf"'
    return response
