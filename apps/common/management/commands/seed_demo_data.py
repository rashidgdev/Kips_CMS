import datetime
from decimal import Decimal

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Department, Roles, StaffProfile, StudentProfile, TeacherProfile, User
from apps.academics.models import Course, CourseOffering, Enrollment, Program, Semester
from apps.attendance.models import AttendanceRecord, LectureSession
from apps.daybook.models import DayBookEntry
from apps.assessments.models import Assessment, AssessmentCategory, Mark
from apps.timetable.models import Room, TimeSlot, TimetableEntry
from apps.finance.models import FeeCategory, FeeStructure, Payment, StudentFeeItem
from apps.finance.services import generate_fee_items_for_semester

DEMO_PASSWORD = 'KipsDemo@2026'


class Command(BaseCommand):
    help = 'Seed idempotent demo data: one user per role, a program/semester/courses, offerings and an enrollment.'

    @transaction.atomic
    def handle(self, *args, **options):
        department = self._create_department()
        program = self._create_program(department)
        semester_1, semester_2 = self._create_semesters(program)
        courses = self._create_courses(program)

        hod_user = self._create_user('hod1', 'Hina', 'Sheikh', Roles.HOD)
        teacher_user = self._create_user('teacher1', 'Ahmed', 'Raza', Roles.TEACHER)
        student_user = self._create_user('student1', 'Bilal', 'Khan', Roles.STUDENT)
        coordinator_user = self._create_user(
            'coordinator1', 'Sara', 'Iqbal', Roles.COORDINATOR, is_staff=True
        )
        accountant_user = self._create_user(
            'accountant1', 'Usman', 'Tariq', Roles.ACCOUNTANT, is_staff=True
        )
        admin_user = self._create_user(
            'admin1', 'Ayesha', 'Malik', Roles.ADMIN, is_staff=True, is_superuser=True
        )

        hod_profile = self._create_teacher_profile(hod_user, 'EMP-HOD-1', department)
        teacher_profile = self._create_teacher_profile(teacher_user, 'EMP-TCH-1', department)
        self._create_staff_profile(coordinator_user, 'EMP-CRD-1')
        self._create_staff_profile(accountant_user, 'EMP-ACC-1')

        department.hod = hod_user
        department.save(update_fields=['hod'])

        student_profile = self._create_student_profile(student_user, program, semester_2)

        offering = self._create_offering(courses[0], semester_2, teacher_profile, coordinator_user)
        offering_2 = self._create_offering(courses[1], semester_2, hod_profile, coordinator_user)

        Enrollment.objects.get_or_create(student=student_profile, course_offering=offering)
        Enrollment.objects.get_or_create(student=student_profile, course_offering=offering_2)

        # Good attendance in CS201, attendance shortage in CS202 - demonstrates both states.
        self._seed_attendance(
            offering, student_profile, teacher_user,
            ['present', 'present', 'present', 'absent', 'present', 'present', 'late', 'present'],
        )
        self._seed_attendance(
            offering_2, student_profile, hod_user,
            ['present', 'absent', 'absent', 'present', 'absent', 'absent', 'present', 'absent'],
        )

        # Verify the first half of CS201's day book entries so both the verify
        # queue and the workload report have something meaningful to show;
        # CS202's entries are left pending for coordinator1 to work through.
        self._verify_daybook_entries(offering, count=4, verified_by=coordinator_user)

        # Strong performance in CS201, weaker in CS202 - demonstrates a
        # realistic mixed GPA and both healthy/at-risk grade states.
        self._seed_assessments(
            offering, student_profile, teacher_user,
            [
                ('Quiz', 'Quiz 1', 10, 10, 8, 25),
                ('Assignment', 'Assignment 1', 20, 10, 17, 20),
                ('Midterm', 'Midterm Exam', 50, 30, 40, 10),
            ],
        )
        self._seed_assessments(
            offering_2, student_profile, hod_user,
            [
                ('Quiz', 'Quiz 1', 10, 10, 5, 25),
            ],
        )

        room_101, lab_1 = self._create_rooms()
        self._seed_timetable(offering, room_101, [1, 3], 'Period 1', coordinator_user)
        self._seed_timetable(offering_2, lab_1, [2, 4], 'Period 2', coordinator_user)

        self._create_fee_structures(program)
        # Semester 1 fully settled; semester 2 tuition partially paid, exam fee
        # unpaid and past due - demonstrates paid/partial/overdue states.
        self._seed_finance(student_profile, semester_1, semester_2, accountant_user)

        self._grant_coordinator_permissions()
        self._grant_accountant_permissions()

        self.stdout.write(self.style.SUCCESS('Demo data seeded successfully.'))
        self.stdout.write('')
        self.stdout.write('Demo login credentials (username / password):')
        for username in ['student1', 'teacher1', 'hod1', 'coordinator1', 'accountant1', 'admin1']:
            self.stdout.write(f'  {username} / {DEMO_PASSWORD}')

    def _create_department(self):
        department, _ = Department.objects.get_or_create(
            code='CS', defaults={'name': 'Computer Science'}
        )
        return department

    def _create_program(self, department):
        program, _ = Program.objects.get_or_create(
            code='BSCS',
            defaults={
                'name': 'BS Computer Science',
                'department': department,
                'total_semesters': 8,
                'degree_level': Program.DegreeLevel.BACHELORS,
            },
        )
        return program

    def _create_semesters(self, program):
        today = datetime.date.today()
        semester_1, _ = Semester.objects.get_or_create(
            program=program,
            number=1,
            academic_year='2025-2026',
            defaults={
                'name': 'Semester 1',
                'start_date': today - datetime.timedelta(days=180),
                'end_date': today - datetime.timedelta(days=30),
                'is_current': False,
            },
        )
        semester_2, _ = Semester.objects.get_or_create(
            program=program,
            number=2,
            academic_year='2025-2026',
            defaults={
                'name': 'Semester 2',
                'start_date': today - datetime.timedelta(days=20),
                'end_date': today + datetime.timedelta(days=140),
                'is_current': True,
            },
        )
        return semester_1, semester_2

    def _create_courses(self, program):
        course_defs = [
            ('CS201', 'Data Structures', 3, 2),
            ('CS202', 'Database Systems', 3, 2),
            ('CS203', 'Object Oriented Programming', 4, 2),
            ('CS204', 'Discrete Mathematics', 3, 2),
        ]
        courses = []
        for code, title, credit_hours, semester_number in course_defs:
            course, _ = Course.objects.get_or_create(
                code=code,
                defaults={
                    'program': program,
                    'title': title,
                    'credit_hours': credit_hours,
                    'semester_number': semester_number,
                },
            )
            courses.append(course)
        return courses

    def _create_user(self, username, first_name, last_name, role, is_staff=False, is_superuser=False):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f'{username}@kipskasur.edu.pk',
                'role': role,
                'is_staff': is_staff,
                'is_superuser': is_superuser,
            },
        )
        if created:
            user.set_password(DEMO_PASSWORD)
            user.save()
        elif user.is_staff != is_staff or user.is_superuser != is_superuser:
            # Demo users are re-synced on every run so changes to seed
            # definitions (e.g. a role gaining admin access) apply to
            # accounts seeded in an earlier run, not just new ones.
            user.is_staff = is_staff
            user.is_superuser = is_superuser
            user.save(update_fields=['is_staff', 'is_superuser'])
        return user

    def _create_teacher_profile(self, user, employee_id, department):
        profile, _ = TeacherProfile.objects.get_or_create(
            user=user,
            defaults={
                'employee_id': employee_id,
                'department': department,
                'designation': 'Lecturer',
                'qualification': 'MS Computer Science',
                'joining_date': datetime.date.today() - datetime.timedelta(days=365),
                'per_lecture_rate': 800,
            },
        )
        return profile

    def _create_staff_profile(self, user, employee_id):
        profile, _ = StaffProfile.objects.get_or_create(
            user=user,
            defaults={'employee_id': employee_id, 'joining_date': datetime.date.today()},
        )
        return profile

    def _create_student_profile(self, user, program, semester):
        profile, _ = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'roll_number': 'BSCS-2025-01',
                'program': program,
                'current_semester': semester,
                'admission_date': datetime.date.today() - datetime.timedelta(days=200),
                'status': StudentProfile.Status.ACTIVE,
            },
        )
        return profile

    def _create_offering(self, course, semester, teacher_profile, assigned_by):
        offering, _ = CourseOffering.objects.get_or_create(
            course=course,
            semester=semester,
            section='A',
            defaults={'teacher': teacher_profile, 'assigned_by': assigned_by},
        )
        return offering

    def _seed_attendance(self, course_offering, student, marked_by, statuses):
        today = datetime.date.today()
        for index, status in enumerate(statuses):
            session_date = today - datetime.timedelta(days=(len(statuses) - index) * 2)
            session, _ = LectureSession.objects.get_or_create(
                course_offering=course_offering,
                date=session_date,
                start_time=datetime.time(9, 0),
                end_time=datetime.time(10, 0),
                defaults={'created_by': marked_by},
            )
            AttendanceRecord.objects.get_or_create(
                session=session,
                student=student,
                defaults={'status': status, 'marked_by': marked_by},
            )
            # Backfilled explicitly (not just via signal) so seeding is correct
            # even if this command runs before the daybook app's signal wiring.
            DayBookEntry.objects.get_or_create(session=session)

    def _verify_daybook_entries(self, course_offering, count, verified_by):
        """Idempotently verify the first `count` entries (by date) for this offering."""
        entries = DayBookEntry.objects.filter(
            session__course_offering=course_offering
        ).order_by('session__date')[:count]
        for entry in entries:
            entry.verified_by = verified_by
            entry.verified_at = timezone.now()
            entry.remarks = 'Verified during demo data seeding.'
            entry.save(update_fields=['verified_by', 'verified_at', 'remarks', 'updated_at'])

    def _seed_assessments(self, course_offering, student, graded_by, items):
        today = datetime.date.today()
        for category_name, title, total_marks, weight_percent, obtained_marks, days_ago in items:
            category = AssessmentCategory.objects.get(name=category_name)
            assessment, _ = Assessment.objects.get_or_create(
                course_offering=course_offering,
                title=title,
                defaults={
                    'category': category,
                    'total_marks': total_marks,
                    'weight_percent': weight_percent,
                    'date': today - datetime.timedelta(days=days_ago),
                    'created_by': graded_by,
                },
            )
            Mark.objects.update_or_create(
                assessment=assessment,
                student=student,
                defaults={'obtained_marks': obtained_marks, 'graded_by': graded_by},
            )

    def _create_rooms(self):
        room_101, _ = Room.objects.get_or_create(
            name='Room 101',
            defaults={'building': 'Main Block', 'capacity': 60, 'room_type': Room.RoomType.CLASSROOM},
        )
        lab_1, _ = Room.objects.get_or_create(
            name='Lab 1',
            defaults={'building': 'CS Block', 'capacity': 30, 'room_type': Room.RoomType.LAB},
        )
        return room_101, lab_1

    def _seed_timetable(self, course_offering, room, day_values, period_label, created_by):
        for day in day_values:
            slot = TimeSlot.objects.get(day_of_week=day, label=period_label)
            TimetableEntry.objects.get_or_create(
                course_offering=course_offering,
                time_slot=slot,
                defaults={'room': room, 'created_by': created_by},
            )

    def _create_fee_structures(self, program):
        tuition, _ = FeeCategory.objects.get_or_create(name='Tuition Fee')
        registration, _ = FeeCategory.objects.get_or_create(name='University Registration Fee')
        exam, _ = FeeCategory.objects.get_or_create(name='Semester Exam Fee')

        FeeStructure.objects.get_or_create(
            program=program, category=tuition, defaults={'amount': 50000, 'is_recurring': True}
        )
        FeeStructure.objects.get_or_create(
            program=program, category=registration, defaults={'amount': 10000, 'is_recurring': False}
        )
        FeeStructure.objects.get_or_create(
            program=program, category=exam, defaults={'amount': 5000, 'is_recurring': True}
        )

    def _seed_finance(self, student, semester_1, semester_2, received_by):
        generate_fee_items_for_semester(student, semester_1)
        generate_fee_items_for_semester(student, semester_2)

        # Semester 1: fully settled.
        for item in StudentFeeItem.objects.filter(student=student, semester=semester_1):
            if not item.payments.exists():
                Payment.objects.create(
                    fee_item=item,
                    amount_paid=item.amount_due,
                    payment_date=item.due_date,
                    payment_method=Payment.Method.BANK_TRANSFER,
                    received_by=received_by,
                )

        # Semester 2: tuition partially paid, exam fee left unpaid (and overdue).
        tuition_item = StudentFeeItem.objects.filter(
            student=student, semester=semester_2, category__name='Tuition Fee'
        ).first()
        if tuition_item and not tuition_item.payments.exists():
            Payment.objects.create(
                fee_item=tuition_item,
                amount_paid=Decimal('30000'),
                payment_date=datetime.date.today() - datetime.timedelta(days=5),
                payment_method=Payment.Method.CASH,
                received_by=received_by,
            )

    def _grant_coordinator_permissions(self):
        group, _ = Group.objects.get_or_create(name=Roles.COORDINATOR.label)
        permissions = Permission.objects.filter(
            content_type__app_label__in=['academics', 'accounts']
        )
        group.permissions.add(*permissions)

    def _grant_accountant_permissions(self):
        group, _ = Group.objects.get_or_create(name=Roles.ACCOUNTANT.label)
        permissions = Permission.objects.filter(content_type__app_label='finance')
        group.permissions.add(*permissions)
