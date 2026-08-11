"""
Renders a student's per-semester progress report ("result card") as a
downloadable PDF - attendance, a breakdown by assessment category
(quiz/assignment/presentation/midterm/final), per-course results, and the
student's photo, so a printed copy can travel with the student the way a
physical report card would.
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
LEFT = 15 * mm
RIGHT = PAGE_W - 15 * mm
CONTENT_W = RIGHT - LEFT


def _header(c, report):
    student = report['student']
    y = PAGE_H - 15 * mm

    if os.path.exists(LOGO_PATH):
        try:
            c.drawImage(LOGO_PATH, LEFT, y - 12 * mm, width=14 * mm, height=14 * mm,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    c.setFont('Helvetica-Bold', 15)
    c.setFillColor(colors.HexColor('#1E3A8A'))
    c.drawString(LEFT + 18 * mm, y - 4 * mm, 'KIPS College Kasur Campus')
    c.setFont('Helvetica', 9.5)
    c.setFillColor(colors.HexColor('#4B5563'))
    c.drawString(LEFT + 18 * mm, y - 9.5 * mm, f'Student Progress Report - {report["semester"]}')

    # Student photo, top-right
    photo_w = photo_h = 24 * mm
    photo_x = RIGHT - photo_w
    photo_y = y - 14 * mm
    if getattr(student.user, 'photo', None):
        try:
            c.drawImage(
                student.user.photo.path, photo_x, photo_y, width=photo_w, height=photo_h,
                preserveAspectRatio=True, anchor='c', mask='auto',
            )
        except Exception:
            pass
    c.setStrokeColor(colors.HexColor('#D1D5DB'))
    c.setLineWidth(0.75)
    c.rect(photo_x, photo_y, photo_w, photo_h, stroke=1, fill=0)

    y -= 20 * mm
    c.setStrokeColor(colors.HexColor('#9CA3AF'))
    c.line(LEFT, y, RIGHT, y)
    y -= 7 * mm

    def field(x_label, x_val, y, label_text, value_text):
        c.setFont('Helvetica', 8.5)
        c.setFillColor(colors.HexColor('#6B7280'))
        c.drawString(x_label, y, label_text)
        c.setFont('Helvetica-Bold', 9.5)
        c.setFillColor(colors.black)
        c.drawString(x_val, y, str(value_text))

    col1_label_x, col1_val_x = LEFT, LEFT + 26 * mm
    col2_label_x, col2_val_x = LEFT + CONTENT_W / 2 - 20 * mm, LEFT + CONTENT_W / 2 + 8 * mm

    field(col1_label_x, col1_val_x, y, 'Student', student.user.get_full_name())
    field(col2_label_x, col2_val_x, y, 'Roll No.', student.roll_number)
    y -= 6 * mm
    field(col1_label_x, col1_val_x, y, 'Program', student.program.name if student.program else '-')
    field(col2_label_x, col2_val_x, y, 'Semester', str(report['semester']))

    return y - 10 * mm


def _section_title(c, y, text):
    c.setFont('Helvetica-Bold', 10.5)
    c.setFillColor(colors.HexColor('#1E3A8A'))
    c.drawString(LEFT, y, text)
    return y - 6 * mm


def _table_row_header(c, y, cols):
    c.setFillColor(colors.HexColor('#EEF2FF'))
    c.rect(LEFT, y - 5 * mm, CONTENT_W, 5 * mm, fill=1, stroke=0)
    c.setFont('Helvetica-Bold', 8.5)
    c.setFillColor(colors.HexColor('#1E3A8A'))
    for text, x, align in cols:
        if align == 'right':
            c.drawRightString(x, y - 3.7 * mm, text)
        else:
            c.drawString(x, y - 3.7 * mm, text)
    return y - 5 * mm


def _attendance_section(c, y, report):
    y = _section_title(c, y, 'Attendance')
    overall = report['attendance_overall']
    c.setFont('Helvetica', 9.5)
    c.setFillColor(colors.black)
    pct = f'{overall["percentage"]}%' if overall['percentage'] is not None else 'No data yet'
    c.drawString(
        LEFT + 2 * mm, y - 4 * mm,
        f'Lectures delivered: {overall["delivered"]}   |   Attended: {overall["attended"]}   |   Overall: {pct}',
    )
    return y - 11 * mm


def _category_section(c, y, report):
    y = _section_title(c, y, 'Assessment Performance')
    col_positions = [
        ('Category', LEFT + 2 * mm, 'left'),
        ('Obtained', LEFT + CONTENT_W * 0.55, 'right'),
        ('Possible', LEFT + CONTENT_W * 0.75, 'right'),
        ('Percentage', RIGHT - 2 * mm, 'right'),
    ]
    y = _table_row_header(c, y, col_positions)
    c.setFont('Helvetica', 9)
    c.setFillColor(colors.black)
    for row in report['category_breakdown']:
        y -= 5.5 * mm
        c.drawString(LEFT + 2 * mm, y + 1.2 * mm, row['name'])
        c.drawRightString(LEFT + CONTENT_W * 0.55, y + 1.2 * mm, f'{row["obtained"]:g}')
        c.drawRightString(LEFT + CONTENT_W * 0.75, y + 1.2 * mm, f'{row["possible"]:g}')
        c.drawRightString(
            RIGHT - 2 * mm, y + 1.2 * mm,
            f'{row["percentage"]}%' if row['percentage'] is not None else '-',
        )
    return y - 8 * mm


def _courses_section(c, y, report):
    y = _section_title(c, y, 'Course-wise Result')
    col_positions = [
        ('Course', LEFT + 2 * mm, 'left'),
        ('Obtained', LEFT + CONTENT_W * 0.55, 'right'),
        ('Possible', LEFT + CONTENT_W * 0.72, 'right'),
        ('Grade', RIGHT - 2 * mm, 'right'),
    ]
    y = _table_row_header(c, y, col_positions)
    c.setFont('Helvetica', 9)
    c.setFillColor(colors.black)
    if not report['course_rows']:
        y -= 5.5 * mm
        c.setFillColor(colors.HexColor('#9CA3AF'))
        c.drawString(LEFT + 2 * mm, y + 1.2 * mm, 'No enrolled courses this semester.')
        return y - 8 * mm
    for row in report['course_rows']:
        y -= 5.5 * mm
        result = row['result']
        c.setFillColor(colors.black)
        c.drawString(LEFT + 2 * mm, y + 1.2 * mm, f'{row["offering"].course.code} - {row["offering"].course.title}')
        c.drawRightString(LEFT + CONTENT_W * 0.55, y + 1.2 * mm, f'{result.total_obtained:g}' if result else '-')
        c.drawRightString(LEFT + CONTENT_W * 0.72, y + 1.2 * mm, f'{result.total_possible:g}' if result else '-')
        c.drawRightString(RIGHT - 2 * mm, y + 1.2 * mm, (result.grade_letter or '-') if result else '-')
    return y - 8 * mm


def _gpa_and_footer(c, y, report):
    if report['semester_gpa'] and report['semester_gpa'].gpa is not None:
        c.setFont('Helvetica-Bold', 11)
        c.setFillColor(colors.HexColor('#1E3A8A'))
        c.drawString(LEFT, y, f'Semester GPA: {report["semester_gpa"].gpa}')
        y -= 10 * mm

    c.setStrokeColor(colors.HexColor('#D1D5DB'))
    c.line(LEFT, y, RIGHT, y)
    y -= 6 * mm
    c.setFont('Helvetica', 7.5)
    c.setFillColor(colors.HexColor('#9CA3AF'))
    c.drawString(LEFT, y, 'This is a system-generated report card from the KIPS Campus Management System.')


def render_progress_report_pdf(report):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setTitle(f'Progress Report - {report["student"].roll_number}')

    y = _header(c, report)
    y = _attendance_section(c, y, report)
    y = _category_section(c, y, report)
    y = _courses_section(c, y, report)
    _gpa_and_footer(c, y, report)

    c.showPage()
    c.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    filename = f'progress_report_{report["student"].roll_number}_{report["semester"]}.pdf'.replace(' ', '_')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
