from django.contrib import messages
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from apps.academics.models import CourseOffering, Enrollment
from apps.accounts.models import Roles
from apps.common.crud import CrudCreateView, CrudDeleteView, CrudListView, CrudUpdateView
from apps.common.middleware import get_profile
from apps.common.permissions import role_required

from .forms import AssessmentCategoryForm, AssessmentForm
from .models import Assessment, AssessmentCategory, CourseResult, Mark, SemesterGPA
from .services import enter_marks_bulk, get_cgpa, get_student_course_overview

STAFF_ROLES = (Roles.COORDINATOR, Roles.ADMIN)


# --- Assessment categories (setup data) -------------------------------------

class AssessmentCategoryListView(CrudListView):
    model = AssessmentCategory
    allowed_roles = STAFF_ROLES
    page_title = 'Assessment Categories'
    list_display = [('name', 'Name'), ('default_weight_percent', 'Default Weight %')]
    add_url_name = 'assessments:category-new'
    edit_url_name = 'assessments:category-edit'
    delete_url_name = 'assessments:category-delete'


class AssessmentCategoryCreateView(CrudCreateView):
    model = AssessmentCategory
    form_class = AssessmentCategoryForm
    allowed_roles = STAFF_ROLES
    page_title = 'Add Assessment Category'
    success_url = reverse_lazy('assessments:categories')
    success_message = 'Assessment category created.'


class AssessmentCategoryUpdateView(CrudUpdateView):
    model = AssessmentCategory
    form_class = AssessmentCategoryForm
    allowed_roles = STAFF_ROLES
    page_title = 'Edit Assessment Category'
    success_url = reverse_lazy('assessments:categories')
    success_message = 'Assessment category updated.'


class AssessmentCategoryDeleteView(CrudDeleteView):
    model = AssessmentCategory
    allowed_roles = STAFF_ROLES
    success_url = reverse_lazy('assessments:categories')
    success_message = 'Assessment category deleted.'


@role_required(Roles.TEACHER, Roles.HOD)
def offering_list(request):
    profile = get_profile(request)
    offerings = profile.course_offerings.select_related('course', 'semester').filter(is_active=True)
    return render(request, 'assessments/offering_list.html', {'offerings': offerings})


def _get_own_offering(request, offering_id):
    profile = get_profile(request)
    return get_object_or_404(CourseOffering, pk=offering_id, teacher=profile)


@role_required(Roles.TEACHER, Roles.HOD)
def assessment_list(request, offering_id):
    offering = _get_own_offering(request, offering_id)
    assessments = offering.assessments.select_related('category').annotate(
        marks_count=Count('marks')
    )
    total_weight = offering.assessments.aggregate(total=Sum('weight_percent'))['total'] or 0
    return render(
        request,
        'assessments/assessment_list.html',
        {'offering': offering, 'assessments': assessments, 'total_weight': total_weight},
    )


@role_required(Roles.TEACHER, Roles.HOD)
def assessment_create(request, offering_id):
    offering = _get_own_offering(request, offering_id)

    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.course_offering = offering
            assessment.created_by = request.user
            assessment.save()
            return redirect('assessments:marks', assessment_id=assessment.pk)
    else:
        form = AssessmentForm()

    return render(request, 'assessments/assessment_form.html', {'offering': offering, 'form': form})


@role_required(Roles.TEACHER, Roles.HOD)
def enter_marks(request, assessment_id):
    profile = get_profile(request)
    assessment = get_object_or_404(
        Assessment, pk=assessment_id, course_offering__teacher=profile
    )

    enrollments = Enrollment.objects.filter(
        course_offering=assessment.course_offering, status=Enrollment.Status.ENROLLED
    ).select_related('student__user')

    existing = {m.student_id: m.obtained_marks for m in assessment.marks.all()}

    if request.method == 'POST':
        raw_value_by_student_id = {
            enrollment.student.pk: request.POST.get(f'marks_{enrollment.student.pk}', '')
            for enrollment in enrollments
        }
        errors = enter_marks_bulk(assessment, raw_value_by_student_id, graded_by=request.user)

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            messages.success(request, 'Marks saved.')
            return redirect('assessments:assessments', offering_id=assessment.course_offering_id)

    rows = [
        {'student': e.student, 'value': existing.get(e.student_id, '')}
        for e in enrollments
    ]
    return render(
        request, 'assessments/enter_marks.html', {'assessment': assessment, 'rows': rows}
    )


@role_required(Roles.STUDENT)
def student_overview(request):
    profile = get_profile(request)
    results = get_student_course_overview(profile)
    # The student's own semester, not "whichever semester happens to be
    # marked current" - a program can have several concurrent current
    # semesters (different cohorts), so semester__is_current isn't specific
    # enough to identify this particular student's semester.
    current_semester_gpa = SemesterGPA.objects.filter(
        student=profile, semester=profile.current_semester
    ).select_related('semester').first()
    cgpa = get_cgpa(profile)
    return render(
        request,
        'assessments/student_overview.html',
        {'results': results, 'current_semester_gpa': current_semester_gpa, 'cgpa': cgpa},
    )


@role_required(Roles.STUDENT)
def student_course_detail(request, offering_id):
    profile = get_profile(request)
    offering = get_object_or_404(
        CourseOffering, pk=offering_id, enrollments__student=profile,
        enrollments__status=Enrollment.Status.ENROLLED,
    )
    result = CourseResult.objects.filter(student=profile, course_offering=offering).first()
    marks = Mark.objects.filter(student=profile, assessment__course_offering=offering).select_related(
        'assessment__category'
    )
    return render(
        request,
        'assessments/student_course_detail.html',
        {'offering': offering, 'result': result, 'marks': marks},
    )
