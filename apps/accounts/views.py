import csv
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy

from apps.common.api_crud_views import ApiCrudDeleteView, ApiCrudFormView, ApiCrudListView
from apps.common.permissions import role_required

from . import imports as bulk_imports
from .forms import (
    ImportUploadForm,
    ProfilePhotoForm,
    StaffCreateForm,
    StaffProfileEditForm,
    StudentCreateForm,
    StudentProfileEditForm,
    StyledPasswordChangeForm,
    TeacherCreateForm,
    TeacherProfileEditForm,
)
from .models import Department, Roles, StaffProfile, StudentProfile, TeacherProfile, User

STAFF_MANAGEMENT_ROLES = (Roles.COORDINATOR, Roles.ADMIN)


# --- Change password ---------------------------------------------------------

class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    form_class = StyledPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('dashboard:redirect')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.must_change_password:
            self.request.user.must_change_password = False
            self.request.user.save(update_fields=['must_change_password'])
        messages.success(self.request, 'Your password has been changed.')
        return response


# --- My profile (photo) -------------------------------------------------

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfilePhotoForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile photo updated.')
            return redirect('accounts:profile')
    else:
        form = ProfilePhotoForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})


# --- Departments (converted to the REST-API-driven CRUD pattern - see
# apps/common/api_crud_views.py, apps/accounts/api_views.py::DepartmentViewSet,
# static/js/core/crud.js) -----------------------------------------------

class DepartmentListView(ApiCrudListView):
    allowed_roles = STAFF_MANAGEMENT_ROLES
    page_title = 'Departments'
    api_list_url_name = 'accounts_api:department-list'
    columns = [('code', 'Code'), ('name', 'Name'), ('hod_label', 'HOD')]
    add_url_name = 'accounts:department-new'
    edit_url_name = 'accounts:department-edit'
    delete_url_name = 'accounts:department-delete'
    created_message = 'Department created.'
    updated_message = 'Department updated.'
    deleted_message = 'Department deleted.'


class DepartmentFormView(ApiCrudFormView):
    """Serves both accounts:department-new (no pk) and accounts:department-edit (pk)."""
    allowed_roles = STAFF_MANAGEMENT_ROLES
    create_page_title = 'Add Department'
    edit_page_title = 'Edit Department'
    api_list_url_name = 'accounts_api:department-list'
    api_detail_url_name = 'accounts_api:department-detail'
    list_url_name = 'accounts:departments'


class DepartmentDeleteView(ApiCrudDeleteView):
    allowed_roles = STAFF_MANAGEMENT_ROLES
    api_detail_url_name = 'accounts_api:department-detail'
    list_url_name = 'accounts:departments'
    title_fields = ('code', 'name')
    title_separator = ' - '


# --- People directory ----------------------------------------------------

@role_required(*STAFF_MANAGEMENT_ROLES)
def people_directory(request):
    role_filter = request.GET.get('role', '')
    department_filter = request.GET.get('department', '')
    query = request.GET.get('q', '').strip()

    users = User.objects.select_related(
        'student_profile__program__department', 'teacher_profile__department', 'staff_profile'
    ).order_by('role', 'first_name')

    if role_filter:
        users = users.filter(role=role_filter)

    if department_filter:
        # A student's "department" is their program's department - StaffProfile
        # has no department of its own (coordinator/accountant/admin are
        # campus-wide, not tied to one).
        users = users.filter(
            Q(teacher_profile__department_id=department_filter)
            | Q(student_profile__program__department_id=department_filter)
        )

    if query:
        users = users.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(username__icontains=query)
            | Q(email__icontains=query)
            | Q(student_profile__roll_number__icontains=query)
            | Q(teacher_profile__employee_id__icontains=query)
            | Q(staff_profile__employee_id__icontains=query)
        )

    users = users.distinct()

    return render(
        request,
        'accounts/people_directory.html',
        {
            'users': users,
            'roles': Roles.choices,
            'role_filter': role_filter,
            'departments': Department.objects.order_by('name'),
            'department_filter': department_filter,
            'query': query,
        },
    )


@role_required(*STAFF_MANAGEMENT_ROLES)
def toggle_active(request, user_id):
    person = get_object_or_404(User, pk=user_id)
    if person.role in (Roles.COORDINATOR, Roles.ACCOUNTANT, Roles.ADMIN) and request.user.role != Roles.ADMIN:
        messages.error(request, 'Only a College Administrator can activate/deactivate staff accounts.')
        return redirect('accounts:people')
    if request.method == 'POST':
        person.is_active = not person.is_active
        person.save(update_fields=['is_active'])
        messages.success(request, f'{person} is now {"active" if person.is_active else "inactive"}.')
    return redirect('accounts:people')


# --- Add person ------------------------------------------------------------

def _person_created_response(request, profile, temp_password):
    return render(request, 'accounts/person_created.html', {
        'profile': profile,
        'temp_password': temp_password,
        'role_label': profile.user.get_role_display(),
    })


@role_required(*STAFF_MANAGEMENT_ROLES)
def student_create(request):
    if request.method == 'POST':
        form = StudentCreateForm(request.POST, request.FILES)
        if form.is_valid():
            profile, temp_password = form.save()
            return _person_created_response(request, profile, temp_password)
    else:
        form = StudentCreateForm()
    return render(request, 'common/generic_form.html', {'form': form, 'page_title': 'Add Student', 'cancel_url': reverse('accounts:people')})


@role_required(*STAFF_MANAGEMENT_ROLES)
def teacher_create(request):
    if request.method == 'POST':
        form = TeacherCreateForm(request.POST, request.FILES)
        if form.is_valid():
            profile, temp_password = form.save()
            return _person_created_response(request, profile, temp_password)
    else:
        form = TeacherCreateForm()
    return render(request, 'common/generic_form.html', {'form': form, 'page_title': 'Add Teacher / HOD', 'cancel_url': reverse('accounts:people')})


@role_required(Roles.ADMIN)
def staff_create(request):
    if request.method == 'POST':
        form = StaffCreateForm(request.POST, request.FILES)
        if form.is_valid():
            profile, temp_password = form.save()
            return _person_created_response(request, profile, temp_password)
    else:
        form = StaffCreateForm()
    return render(request, 'common/generic_form.html', {'form': form, 'page_title': 'Add Staff', 'cancel_url': reverse('accounts:people')})


# --- Edit profile ------------------------------------------------------------

@role_required(*STAFF_MANAGEMENT_ROLES)
def student_edit(request, profile_id):
    profile = get_object_or_404(StudentProfile, pk=profile_id)
    if request.method == 'POST':
        form = StudentProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student profile updated.')
            return redirect('accounts:people')
    else:
        form = StudentProfileEditForm(instance=profile)
    return render(request, 'common/generic_form.html', {'form': form, 'page_title': f'Edit {profile}', 'cancel_url': reverse('accounts:people')})


@role_required(*STAFF_MANAGEMENT_ROLES)
def teacher_edit(request, profile_id):
    profile = get_object_or_404(TeacherProfile, pk=profile_id)
    if request.method == 'POST':
        form = TeacherProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher profile updated.')
            return redirect('accounts:people')
    else:
        form = TeacherProfileEditForm(instance=profile)
    return render(request, 'common/generic_form.html', {'form': form, 'page_title': f'Edit {profile}', 'cancel_url': reverse('accounts:people')})


@role_required(Roles.ADMIN)
def staff_edit(request, profile_id):
    profile = get_object_or_404(StaffProfile, pk=profile_id)
    if request.method == 'POST':
        form = StaffProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Staff profile updated.')
            return redirect('accounts:people')
    else:
        form = StaffProfileEditForm(instance=profile)
    return render(request, 'common/generic_form.html', {'form': form, 'page_title': f'Edit {profile}', 'cancel_url': reverse('accounts:people')})


# --- Bulk import from Excel -------------------------------------------------

def _workbook_response(workbook, filename):
    buffer = io.BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def _run_import(request, import_func, columns, session_key, results_url_name, page_title, template_url_name):
    if request.method == 'POST':
        form = ImportUploadForm(request.POST, request.FILES)
        if form.is_valid():
            created, errors = import_func(form.cleaned_data['file'])
            request.session[session_key] = {'created': created, 'errors': errors}
            return redirect(results_url_name)
    else:
        form = ImportUploadForm()
    return render(
        request,
        'accounts/import_form.html',
        {
            'form': form,
            'page_title': page_title,
            'columns': columns,
            'template_url': reverse(template_url_name),
            'cancel_url': reverse('accounts:people'),
        },
    )


def _import_results(request, session_key, title, csv_url_name):
    data = request.session.get(session_key)
    if not data:
        messages.info(request, 'No recent import results to show.')
        return redirect('accounts:people')
    return render(
        request,
        'accounts/import_results.html',
        {
            'title': title,
            'created': data['created'],
            'errors': data['errors'],
            'csv_url': reverse(csv_url_name) if data['created'] else None,
        },
    )


def _import_credentials_csv(request, session_key, filename_prefix):
    data = request.session.get(session_key)
    if not data or not data['created']:
        messages.info(request, 'No credentials available to download.')
        return redirect('accounts:people')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename_prefix}_credentials.csv"'
    writer = csv.writer(response)
    writer.writerow(['Row', 'Username', 'Name', 'Identifier', 'Temporary Password'])
    for row in data['created']:
        writer.writerow([row['row'], row['username'], row['name'], row['identifier'], row['password']])

    del request.session[session_key]
    return response


@role_required(*STAFF_MANAGEMENT_ROLES)
def student_import(request):
    return _run_import(
        request, bulk_imports.import_students, bulk_imports.STUDENT_COLUMNS,
        'student_import_results', 'accounts:student-import-results', 'Import Students',
        'accounts:student-import-template',
    )


@role_required(*STAFF_MANAGEMENT_ROLES)
def student_import_results(request):
    return _import_results(request, 'student_import_results', 'Student Import Results', 'accounts:student-import-csv')


@role_required(*STAFF_MANAGEMENT_ROLES)
def student_import_csv(request):
    return _import_credentials_csv(request, 'student_import_results', 'students')


@role_required(*STAFF_MANAGEMENT_ROLES)
def student_import_template(request):
    wb = bulk_imports.build_template_workbook(bulk_imports.STUDENT_COLUMNS)
    return _workbook_response(wb, 'student_import_template.xlsx')


@role_required(*STAFF_MANAGEMENT_ROLES)
def teacher_import(request):
    return _run_import(
        request, bulk_imports.import_teachers, bulk_imports.TEACHER_COLUMNS,
        'teacher_import_results', 'accounts:teacher-import-results', 'Import Teachers',
        'accounts:teacher-import-template',
    )


@role_required(*STAFF_MANAGEMENT_ROLES)
def teacher_import_results(request):
    return _import_results(request, 'teacher_import_results', 'Teacher Import Results', 'accounts:teacher-import-csv')


@role_required(*STAFF_MANAGEMENT_ROLES)
def teacher_import_csv(request):
    return _import_credentials_csv(request, 'teacher_import_results', 'teachers')


@role_required(*STAFF_MANAGEMENT_ROLES)
def teacher_import_template(request):
    wb = bulk_imports.build_template_workbook(bulk_imports.TEACHER_COLUMNS)
    return _workbook_response(wb, 'teacher_import_template.xlsx')
