# KIPS College Kasur Campus - Campus Management System

A Django-based Campus Management System (CMS) for KIPS College Kasur Campus. This
repository currently implements:

- **Phase 1**: project scaffolding, the full database schema, and
  authentication/role-based access control (RBAC).
- **Module 2 - Attendance**: teachers record subject-wise attendance per
  lecture; students see live attendance %, lecture counts, and shortage
  warnings.
- **Module 3 - Faculty Day Book & Workload Tracking**: every lecture logged
  in Attendance automatically becomes a day book entry; Coordinators/Admins
  verify entries and pull a monthly payroll workload report (CSV export +
  persisted snapshot) based on each teacher's per-lecture rate.
- **Module 4 - Assessments**: teachers create quizzes/assignments/
  presentations/midterms per course and enter marks; students get a live
  obtained/total, percentage, and letter grade per course plus semester
  GPA and overall CGPA, all recalculated automatically the moment a mark
  is saved.
- **Module 5 - Intelligent Timetable**: Coordinators/Admins place classes
  into a weekly day x period grid per semester; the system blocks
  teacher and room double-booking in real time (v1 is assisted scheduling,
  not a full auto-solver, as agreed). Teachers and students get a
  read-only view of their own weekly schedule.
- **Module 6 - Fee & Financial Management**: each program has a fee
  package (tuition, one-time registration, recurring exam fee);
  Accountants/Admins generate a student's fee items per semester and
  record payments against them, with outstanding balance computed live.
  Students see their own fee status and full payment history. Accountants
  can also issue a printable **fee challan** (3-copy bank/college/student
  voucher PDF) per student per semester.
- **Module 7 - Dashboards & Reporting**: a central Reports hub (Attendance,
  Academic Performance, Semester Merit List, plus links to the Faculty
  Workload and Financial reports) with Excel and PDF export everywhere a
  CSV export previously existed alone; role dashboards enriched with
  live cross-module stats (student CGPA/GPA/attendance, teacher's today's
  classes).
- **Module 8 - Administration Portal**: every setup/reference-data workflow
  that previously required the Django Admin Panel now has a proper screen
  in the portal itself - adding students/teachers/staff at admission,
  Departments, Programs, Semesters, Courses, Faculty Assignments,
  Enrollments, Fee Categories/Structures, Rooms/Time Slots, and Assessment
  Categories. The Django Admin Panel is no longer part of any normal
  workflow (kept only as an Admin-only fallback). Students and Teachers can
  also be **bulk-imported from an Excel (.xlsx) file** instead of being
  added one at a time.

All 7 modules from the original spec, plus RBAC, are now built, and all
day-to-day staff actions run through this portal rather than `/admin/`.

## Tech stack

- Django 6 (Python 3.13+), Django templates (no separate frontend framework)
- SQLite for local development (swappable via `DATABASE_URL`)
- Tailwind CSS via [django-tailwind](https://github.com/timonweb/django-tailwind),
  using its **standalone binary** mode - no Node.js/npm required
- `django-environ` for environment-based settings, `whitenoise` for static files

## Branding assets

`static/images/` holds the campus logo and a background watermark, sourced from
the official KIPS Kasur Campus assets and cropped/compressed with Pillow
(`kips-logo-icon.png` for the nav badge and login card, `kips-logo-full.png`
for the footer wordmark, `campus-watermark.jpg` as a low-opacity fixed
background applied campus-wide in `base.html`/`base_auth.html`). All three are
small enough (~340 KB total) to not affect page load.

## Project structure

```
config/                  Django project settings/urls (config/settings/base.py, dev.py, prod.py)
apps/
  common/                Shared abstract models, RBAC permissions/middleware, generic CRUD views (crud.py),
                         Tailwind form mixin (forms.py), Excel/PDF export helpers, seed command
  accounts/               Custom User, Roles, Department, Student/Teacher/Staff profiles, auth,
                         Department/People CRUD screens
  academics/              Program, Semester, Course, CourseOffering, Enrollment + their CRUD screens
  attendance/              LectureSession, AttendanceRecord, attendance stats (services.py)
  daybook/                 DayBookEntry, MonthlyWorkloadSnapshot, workload stats (services.py)
  assessments/             AssessmentCategory, Assessment, Mark, CourseResult, SemesterGPA, grading (services.py)
  timetable/               TimeSlot, Room, TimetableEntry, conflict checking + grid builder (services.py)
  finance/                 FeeCategory, FeeStructure, StudentFeeItem, Payment, balance calc (services.py)
  reports/                 Cross-module Attendance/Academic/Merit List reports + Excel/PDF export
  dashboard/               Role-based dashboard views + the Administration portal hub
templates/                Project-wide templates (base.html, login, per-role dashboards,
                         common/generic_{list,form,confirm_delete}.html for CRUD screens)
theme/                     Generated by django-tailwind (Tailwind entry CSS + compiled output)
```

## Setup

1. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   The defaults work out of the box for local development (SQLite, `DEBUG=True`).

4. **Run migrations**

   ```bash
   python manage.py migrate
   ```

5. **Build Tailwind CSS** (downloads the standalone `tailwindcss` binary on first run)

   ```bash
   python manage.py tailwind install
   python manage.py tailwind build
   ```

6. **Seed demo data** (idempotent - safe to re-run)

   ```bash
   python manage.py seed_demo_data
   ```

7. **Run the app**

   ```bash
   # Runs the Django dev server and the Tailwind watcher together
   python manage.py tailwind dev
   ```

   Or run them separately in two terminals:

   ```bash
   python manage.py runserver
   python manage.py tailwind start   # rebuilds CSS on template/class changes
   ```

   Visit http://127.0.0.1:8000/accounts/login/

## Demo credentials

All seeded users share the password `KipsDemo@2026`.

| Username       | Role                  |
|----------------|-----------------------|
| `student1`     | Student                |
| `teacher1`     | Teacher                 |
| `hod1`         | Head of Department      |
| `coordinator1` | Campus Coordinator      |
| `accountant1`  | Accountant               |
| `admin1`       | College Administrator (superuser) |

`admin1` and `coordinator1` also have Django admin (`/admin/`) access, for
managing Programs, Semesters, Courses, Faculty assignments, and Enrollments
until dedicated CRUD screens are built. `accountant1` similarly has admin
access scoped to the Finance app (fee categories/structures).

`student1` is enrolled in two courses with pre-seeded attendance history to
demo both states: CS201 (87.5%, healthy) and CS202 (37.5%, shortage warning).
CS201's first four lectures are pre-verified in the day book; the rest
(including all of CS202) are left pending so `coordinator1` has a real
verify queue to work through. Grade-wise, CS201 is seeded strong (~82%, A-)
and CS202 weak (50%, D), giving a mixed semester GPA (~2.35) rather than a
flat A/A student. CS201 meets Mon/Wed Period 1 in Room 101 (`teacher1`) and
CS202 meets Tue/Thu Period 2 in Lab 1 (`hod1`), so both `student1`'s and the
teachers' `/timetable/` views show a populated weekly grid out of the box.
Financially, `student1`'s Semester 1 fees (tuition, registration, exam) are
fully paid; Semester 2 tuition is partially paid and the exam fee is unpaid
and past due - so `/finance/my/` shows all three states (paid, partial,
overdue) at once.

## RBAC design

- `apps/accounts/models/user.py` defines a custom `User` with a `role` field
  (`Roles`: STUDENT, TEACHER, HOD, COORDINATOR, ACCOUNTANT, ADMIN). Role-specific
  data lives in separate profile tables (`StudentProfile`, `TeacherProfile`,
  `StaffProfile`), not sparse columns on `User`.
- Authorization is centralized in `apps/common/permissions.py`:
  `role_required(*roles)` for function views, `RoleRequiredMixin` for
  class-based views. No view should hand-roll `if request.user.role == ...` checks.
- `apps/common/middleware.py` (`RoleContextMiddleware`) attaches `request.role`
  and a cached `request.profile` for convenience - it is context only, not the
  authorization gate.
- `apps/common/context_processors.py` exposes `role`, `role_display`, and
  `nav_links` (from a per-role `NAV_CONFIG` dict) to every template, so
  `base.html` renders navigation without `{% if role == "..." %}` chains.
- Each `User` is auto-assigned to a matching Django `Group` on save
  (`apps/accounts/signals.py`), enabling fine-grained `has_perm()` checks
  layered on top of the coarse role field later if needed.

### Self-service password change

- Every account, whether created one-at-a-time or via bulk Excel import (see
  Module 8), starts with a system-generated temporary password and
  `User.must_change_password=True`.
- `apps/common/middleware.py::ForcePasswordChangeMiddleware` redirects any
  authenticated request from such a user to `/accounts/password/change/`
  until they set their own password - the only exempt paths are the
  change-password page itself, logout, and static/media files, so there's no
  way to use the portal with a temporary password still active.
- `/accounts/password/change/` (`ChangePasswordView`) wraps Django's built-in
  `PasswordChangeView`; on success it clears `must_change_password` and keeps
  the user's session alive (no forced re-login). Any user can also reach this
  page any time via the account menu in the top nav to change their password
  voluntarily, not just when forced.

### Profile photos

- Every `User` (any role) has an optional `photo` `ImageField`. Users upload
  their own photo any time from `/accounts/profile/` (the account menu in the
  top nav); a Coordinator/Admin can also set it at creation time on the Add
  Student/Teacher/Staff forms.
- The photo appears in the top nav avatar, the people directory, the
  student-progress-report screen, and on the downloadable result card PDF
  (see Module 7). In dev, uploaded files are served from `MEDIA_ROOT` via
  `config/urls.py`'s `static()` helper (only active when `DEBUG=True` -
  production serves `/media/` some other way, e.g. Nginx/S3).

## Attendance (Module 2)

- `apps/attendance/models.py`: `LectureSession` (one per lecture actually
  delivered) and `AttendanceRecord` (per-student status per session:
  present/absent/leave/late). Attendance % is computed on read
  (`apps/attendance/services.py`), not stored, so it's never stale.
- **Teacher/HOD flow**: `/attendance/offerings/` lists their own course
  offerings -> `/sessions/` lists lecture sessions for one offering, with a
  "New Lecture Session" action -> creating a session redirects straight into
  marking attendance for every enrolled student (defaults to Present,
  editable, re-visitable to correct later).
- **Student flow**: `/attendance/my/` shows delivered/attended/absent/% per
  enrolled course, flagging any course below `ATTENDANCE_SHORTAGE_THRESHOLD`
  (default 75%, configurable via `.env`) with a shortage warning; drill into
  `/attendance/my/<course_offering_id>/` for the full daily log.
- Ownership is enforced per-request (`CourseOffering.objects.get(pk=..., teacher=profile)`),
  so a teacher gets a 404 (not just 403) on another teacher's offering -
  no cross-teacher data leakage.

## Faculty Day Book & Workload Tracking (Module 3)

- `apps/daybook/models.py`: `DayBookEntry` wraps a `LectureSession`
  one-to-one and adds a verification workflow (`verified_by`, `verified_at`,
  `remarks`) rather than duplicating "a lecture happened" as separate data -
  attendance and payroll can never disagree on lecture counts.
- A signal (`apps/daybook/signals.py`) auto-creates a `DayBookEntry` every
  time a `LectureSession` is created in the Attendance module - teachers
  don't do any extra data entry for the day book to populate.
- **Teacher/HOD flow**: `/daybook/` shows their own lecture history with a
  Verified/Pending badge per entry, plus a live summary card (lectures this
  month, verified count, rate, estimated pay).
- **Coordinator/Admin flow**: `/daybook/verify/` lists all pending entries
  campus-wide with a one-click Verify action (optional remarks);
  `/daybook/workload/` is the payroll report - per teacher, delivered vs.
  verified lecture counts for a selected month, rate, and computed amount
  (**verified lectures only** count toward pay, so unverified/disputed
  entries can't inflate payroll). Includes a "Generate Payroll Snapshot"
  action that persists an auditable `MonthlyWorkloadSnapshot` per
  teacher/month, and a CSV export for handing off to payroll.

## Assessments (Module 4)

- `apps/assessments/models.py`: `AssessmentCategory` (Quiz/Assignment/
  Presentation/Midterm/Final, seeded via a data migration with sensible
  default weights), `Assessment` (one graded item in a course, with its own
  `total_marks` and `weight_percent`), `Mark` (one student's score on one
  assessment). `CourseResult` and `SemesterGPA` are cached aggregates,
  recalculated automatically by a signal every time a `Mark` is saved or
  deleted (`apps/assessments/signals.py` -> `services.py`) - never stale,
  never manually triggered.
- **Grading math**: course percentage is the weight-normalized average of
  `obtained/total` across only the assessments graded so far (an ungraded
  midterm doesn't drag the percentage down as if it were a zero); an
  HEC-style scale (`GRADE_SCALE` in `services.py`) maps percentage to a
  letter grade and grade point; semester GPA is the credit-hour-weighted
  average grade point across graded courses in that semester; CGPA is the
  same weighted average across all semesters (computed on read, not stored).
- **Teacher/HOD flow**: `/assessments/offerings/` -> `/offerings/<id>/`
  lists assessments for one course with the total weight assigned so far ->
  "New Assessment" -> creating one redirects straight into entering marks
  for every enrolled student (blank = not graded yet; leaving it blank on a
  previously graded student un-grades them). Marks are validated against
  `0 <= obtained <= total_marks` server-side.
- **Student flow**: `/assessments/my/` - CGPA and current-semester GPA cards
  plus one row per enrolled course (obtained/possible, percentage, letter
  grade), even before anything is graded; drill into
  `/assessments/my/<course_offering_id>/` for the full assessment-by-
  assessment breakdown.

## Intelligent Timetable (Module 5)

- `apps/timetable/models.py`: `TimeSlot` (a specific weekly day+period, e.g.
  "Monday 09:00-10:00" - 25 standard Mon-Fri slots are pre-seeded via a data
  migration so scheduling works immediately), `Room`, `TimetableEntry`
  (course offering + room + time slot). Room double-booking is a hard
  DB-level `unique_together(room, time_slot)` constraint; the ModelForm's
  automatic uniqueness check is deliberately disabled in favor of
  `services.check_conflicts()`, which reports both room *and* teacher
  conflicts with a specific, actionable message instead of a generic
  "already exists" error.
- **Concurrent-semester correctness**: several programs/semesters run at
  the same time in this system, so a teacher conflict is checked against
  every *currently running* semester (`is_current=True`) plus the semester
  being edited - not just entries within one semester - otherwise two
  different programs could double-book the same teacher without either
  coordinator noticing.
- **Coordinator/Admin flow**: `/timetable/` - pick a semester, see its full
  week grid, "+ Schedule a Class" to place a course offering into a
  room/time slot (rejected with a specific error on conflict), "Remove" to
  unschedule. `/timetable/semester/<id>/schedule/` is the assignment form.
- **Teacher/HOD and Student flows**: `/timetable/mine/` and `/timetable/my/`
  are read-only grids scoped to the logged-in user's own current-semester
  classes (by teaching assignment or enrollment respectively) - they share
  the same grid renderer as the coordinator's view via
  `templates/timetable/_grid.html`.
- Known v1 limitation (matches the earlier-agreed scope): only teacher and
  room conflicts are checked. A student having two different enrolled
  courses scheduled in the same slot is not yet flagged.

### Generate Time Slots

- Adding every period one at a time was tedious, so `/timetable/timeslots/generate/`
  ("Generate Time Slots" button on the Time Slots list) builds a whole day's
  periods from three inputs: start of the working day, end of the working
  day, and number of lectures per day (plus an optional
  break-between-lectures field, default 0 for back-to-back periods) -
  applied to every selected working day at once. Lecture length is **not**
  entered directly - `TimeSlotGeneratorForm.clean()` computes it by
  dividing the working day span (minus any breaks) evenly across the
  requested number of lectures, e.g. an 08:00-14:00 day with 6 lectures
  and no breaks becomes six 1-hour periods automatically.
  `apps/timetable/services.py::generate_time_slots()` then walks forward
  from the start time placing each period, labeling them "Period 1",
  "Period 2", etc.
- Validated before anything is created: if the requested lecture count and
  breaks would leave less than 5 minutes per lecture, the form rejects it
  with a specific message instead of creating unreasonably short periods.
- **Safe to re-run**: each period is created via `get_or_create()` on
  `(day_of_week, start_time, end_time)`, so generating again (e.g. after
  deciding to add Sunday, or after editing one period by hand) only adds
  what's missing - existing periods, including the pre-seeded reference
  ones, are left untouched.

## Fee & Financial Management (Module 6)

- `apps/finance/models.py`: `FeeCategory` (Tuition/Registration/Exam Fee -
  simple lookup table), `FeeStructure` (the standard per-program package -
  one row per program+category, `is_recurring` decides whether it's charged
  every semester or once at admission), `StudentFeeItem` (an actual charge
  assigned to one student for one semester), `Payment` (one payment against
  one fee item). Simplified from the original schema sketch: `Payment` has
  no separate `student` FK (derived via `fee_item.student` - one less place
  for the two to drift out of sync) and no stored `receipt_number` (each
  payment's own primary key *is* its receipt number, displayed as
  "Receipt #12" - avoids a fragile two-phase-save just to generate a
  redundant unique string).
- **Fee generation**: `services.generate_fee_items_for_semester()` reads the
  student's program `FeeStructure` and creates their `StudentFeeItem`s for a
  given semester - idempotent, and one-time items (registration fee) are
  only ever charged once per student across their entire academic history,
  not once per semester.
- **Balance, never stored**: outstanding balance/status (paid, partial,
  overdue, unpaid) is computed on read from a fee item's payments, same
  pattern as attendance % and course grades elsewhere in this project -
  status flips from Overdue to Paid the instant a payment is recorded, with
  no separate "recalculate" step.
- **Accountant/Admin flow**: `/finance/students/` - every student with
  total due/paid/outstanding (+ CSV export) -> `/finance/students/<id>/` -
  "Generate Fee Items" for their current semester, a table of fee items with
  a "Record Payment" action per outstanding item. Payments are rejected
  server-side if `amount_paid` would exceed the item's remaining balance.
- **Student flow**: `/finance/my/` - total due/paid/outstanding cards plus
  the full fee item history with status badges.

### Fee Challans

- `apps/finance/models.py`: `Challan` (a formal payment voucher covering a
  student's outstanding fee items for one semester) and `ChallanLine` (each
  covered fee item, with its outstanding **amount frozen at issue time** -
  so a reprinted challan always matches what was originally handed to the
  student, even if fee items change later). `challan_number` is generated
  once (`KIPS-{year}-{id:06d}`) and never changes.
- **No accidental duplicates**: `services.generate_challan()` checks for an
  already-active, unpaid challan for the same student+semester before
  creating a new one - clicking "Generate Challan" twice reuses the
  existing challan (same number, same amount) instead of issuing two live
  vouchers for the same dues. To reissue with a fresh number (e.g. the
  student lost it), cancel the old one first (`/finance/challans/<id>/cancel/`).
- **Status, computed on read** (same pattern as everything else in this
  module): a challan is "Paid" the moment every fee item it covers is
  settled, however that happened - no separate payment-to-challan
  bookkeeping required.
- **The PDF itself** (`apps/finance/challan_pdf.py`): a hand-built
  `reportlab` canvas layout (not the generic table exporter, since this is
  a formatted voucher, not a data export) - one A4 page split into three
  identical copies (**Bank / College / Student**), each with the KIPS
  logo, challan number, student/program/semester details, the fee
  breakdown table, total, and signature lines - matching the standard
  paper challan format used by Pakistani educational institutions.
- **Access**: Accountant/Admin generate and manage challans from a
  student's fee detail page or the campus-wide `/finance/challans/` list;
  a student can view and download their own challans' PDFs from
  `/finance/my/` (ownership is enforced on the PDF endpoint itself, not
  just the page - a student gets 403 on another student's challan even via
  the direct PDF URL).

## Dashboards & Reporting (Module 7)

- **Excel/PDF export, everywhere a report exists**: `apps/common/exports.py`
  has two format-agnostic helpers - `export_excel()` (openpyxl) and
  `export_pdf()` (reportlab, landscape A4, styled table) - so every report
  in the system exports the same way instead of each app hand-rolling its
  own. Retrofitted onto the Day Book payroll report and the Finance fee
  summary (previously CSV-only), and used natively by every new report
  below.
- **Reports hub** (`/reports/`): a role-scoped landing page linking to every
  report in the system - the three built in this module plus the
  already-existing Faculty Workload, Timetable, and Financial reports, so
  staff don't need to remember which app each report lives in.
- **Attendance Report** (`/reports/attendance/`) and **Academic Performance
  Report** (`/reports/academic/`): pick a course, get a per-student
  gradesheet/attendance sheet. Reuses the exact same `get_student_course_stats()`
  (attendance) and `CourseResult` (assessments) data the student-facing
  pages already show - no separate reporting data model, no risk of the
  report ever disagreeing with what a student sees on their own dashboard.
- **Semester Merit List** (`/reports/merit-list/`, Coordinator/Admin only):
  every student in a semester ranked by GPA.
- **Ownership scoping carries into reports**: Teacher/HOD can only run
  Attendance/Academic reports against their *own* course offerings
  (enforced server-side, including on the export endpoints, not just the
  HTML view - confirmed a teacher gets 404 on another teacher's course
  even via the direct export URL); Coordinator/Admin can report on any
  course; the Merit List is Coordinator/Admin only.

### Student Progress Reports (result cards)

- `/reports/progress/students/` (Teacher/HOD/Coordinator/Admin): search any
  student by roll number or name, then open their **result card** -
  combining attendance %, a breakdown by assessment category
  (Quiz/Assignment/Presentation/Midterm/Final), per-course results, and
  Semester GPA in one screen, with the student's photo shown alongside.
  `apps/reports/services.py::get_student_progress_report()` computes this by
  reusing the same attendance/assessment data every other page already
  shows - no separate aggregate table to keep in sync.
- **Downloadable PDF** (`apps/reports/progress_pdf.py`, reportlab
  canvas-drawn, not the generic tabular exporter - this one has a header,
  the student's photo, and multiple sections on one page): the result card
  a student or teacher can save/print, matching the "photo + attendance +
  category-wise marks, downloadable" requirement.
- **Self-service**: a student reaches their own result card from "My
  Grades" -> "My Progress Report" (`/reports/progress/my/`), which resolves
  to their own profile - no way to view or download anyone else's.
- **Ownership enforced on the PDF endpoint itself**, exactly like the fee
  challan PDF: a student gets 403 on another student's report even via the
  direct PDF URL; Teacher/HOD/Coordinator/Admin can open any student's.
- **Dashboards enriched with live cross-module stats**: the student
  dashboard now shows CGPA, current-semester GPA, and overall attendance %
  (pulled from the Assessments and Attendance services); the teacher
  dashboard shows today's classes pulled from the Timetable.

## Administration Portal (Module 8)

Every workflow that previously required going to `/admin/` (the Django
Admin Panel) now has a proper screen in the portal itself, reachable from
one **Administration** hub (`/administration/`, role-scoped by section).

- **Generic CRUD infrastructure** (`apps/common/crud.py`,
  `apps/common/forms.py`): `CrudListView`/`CrudCreateView`/`CrudUpdateView`/
  `CrudDeleteView` wrap Django's generic class-based views with
  `RoleRequiredMixin` and three shared templates
  (`templates/common/generic_{list,form,confirm_delete}.html`), and
  `TailwindFormMixin` auto-applies input styling to every field so a
  ModelForm never needs a hand-written `widgets={}` dict. Nine of the
  eleven new screens below (everything except adding a person and
  scheduling a class, which have real business logic) are ~15-line
  `ListView`/`CreateView`/`UpdateView`/`DeleteView` subclasses on top of
  this - a `list_display = [(attr, label), ...]` config plus a
  `get_attr` template filter (`apps/common/templatetags/common_extras.py`)
  renders arbitrary columns without a bespoke list template per model.
- **People** (`/accounts/people/`, Coordinator/Admin): add a Student,
  Teacher/HOD, or (Admin-only) Staff account. Each "add person" form
  combines the `User` account fields with the role-specific profile
  (`StudentProfile`/`TeacherProfile`/`StaffProfile`) in one submit, creates
  both records, generates a random temporary password, sets
  `must_change_password=True` (a field that existed in the schema since
  Phase 1 but was never wired up until now), and shows the password once
  in a success message for the coordinator to relay securely - it is never
  stored or shown again. Only a College Administrator can create
  Coordinator/Accountant/Admin accounts (privilege escalation guard);
  Coordinators can create Students and Teachers/HODs.
- **Academics** (`/academics/...`, Coordinator/Admin): Programs, Semesters,
  Courses, **Faculty Assignments** (`CourseOffering` - the core "assign a
  course to a teacher for a semester" workflow flagged as admin-only back
  in Phase 1), and Enrollments. Creating a Faculty Assignment auto-fills
  `assigned_by` with the logged-in coordinator, same as the old admin-only
  path did.
- **Setup data**: Departments (accounts), Rooms/Time Slots (timetable),
  Assessment Categories (assessments), Fee Categories/Fee Structures
  (finance, Accountant/Admin only) - all plain CRUD via the shared
  infrastructure above.
- **People directory** (`/accounts/people/`) also handles account
  lifecycle: activate/deactivate any user, with deactivating a
  Coordinator/Accountant/Admin account restricted to Admin only (a
  Coordinator can't lock out another Coordinator or an Accountant).
- The Django Admin Panel remains registered (`/admin/`) as an Admin-only
  fallback for anything not covered above, but is no longer part of any
  normal Coordinator/Accountant workflow - removed from their nav
  entirely.

### Bulk Import from Excel

- `apps/accounts/imports.py`: `import_students()` / `import_teachers()`
  parse an uploaded `.xlsx` (via `openpyxl`) and create accounts row by
  row - each row is its own `transaction.atomic()` block, so one bad row
  (duplicate username, unknown program code, malformed date, etc.) is
  skipped with a specific reason without rolling back the rows before or
  after it. Column headers are matched case-insensitively and can appear
  in any order; a duplicate username/roll-number/employee-ID is caught
  both against the database *and* against earlier rows already processed
  in the same file.
- **Download-the-template-first UX**: `/accounts/people/students/import/`
  and `.../teachers/import/` show the exact expected columns (required vs.
  optional, with a one-line hint each) and a "Download Template" button
  that generates a starter `.xlsx` on the fly from the same column
  definitions the parser uses - the template can never drift out of sync
  with what the importer actually accepts.
- **Results, not a silent all-or-nothing**: after upload, a results page
  shows exactly which rows were created (with their generated temporary
  password) and which were skipped and why. Since 30-50 temporary
  passwords aren't practical to copy by hand, they're also available as a
  **one-time CSV download** - generated from data held in the session
  (never written to the database in plaintext), and the session key is
  cleared the moment the CSV is downloaded.
- **Scope, deliberately**: Coordinator/Admin can bulk-import Students and
  Teachers/HODs, matching who can add them individually. Bulk-creating
  Coordinator/Accountant/Admin accounts from a spreadsheet is deliberately
  *not* offered - those stay individual, Admin-only, same privilege-escalation
  guard as the single "Add Staff" screen.

A real bug was caught and fixed while building this: Django's
`CreateView.get_success_url()` calls `self.object.__dict__` internally (to
support `.format()` placeholders in `success_url`), but `self.object` is
`None` until the form is actually saved - calling it while rendering the
*initial empty form* crashed every single "Add ___" screen with an
`AttributeError`. Fixed by having the shared CRUD base read
`self.success_url` directly for the Cancel link instead of calling
`get_success_url()`. Confirmed fixed by exercising the full
create/edit/delete lifecycle end-to-end for a real record (a Room) after
the fix, not just checking the page loaded.

Every module from the original spec - Course/Semester Management,
Attendance, Faculty Day Book, Assessments, Timetable, Finance,
Dashboards & Reporting, and the Administration Portal - is fully
implemented, on top of the Phase 1 authentication/RBAC foundation, with
all day-to-day staff workflows running through this portal rather than
the Django Admin Panel. Two client-requested additions on top of the
original spec are also in: **fee challan generation** (Module 6) and
**bulk Excel import** for Students/Teachers (Module 8).
