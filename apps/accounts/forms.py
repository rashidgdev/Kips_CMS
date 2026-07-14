from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from apps.common.forms import INPUT_CLASSES, TailwindFormMixin

from .models import Department, Roles, StaffProfile, StudentProfile, TeacherProfile, User


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': INPUT_CLASSES, 'autofocus': True})
        self.fields['password'].widget.attrs.update({'class': INPUT_CLASSES})


class StyledPasswordChangeForm(TailwindFormMixin, PasswordChangeForm):
    pass


class ImportUploadForm(TailwindFormMixin, forms.Form):
    file = forms.FileField(label='Excel file (.xlsx)')

    def clean_file(self):
        uploaded = self.cleaned_data['file']
        if not uploaded.name.lower().endswith('.xlsx'):
            raise forms.ValidationError('Please upload a .xlsx file (Excel 2007 or later).')
        return uploaded


class DepartmentForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'hod']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hod'].queryset = User.objects.filter(role=Roles.HOD)
        self.fields['hod'].required = False
        self.fields['hod'].help_text = (
            'Optional - leave blank for now. Create the department first, add the '
            'HOD as a teacher assigned to it, then come back and edit this '
            'department to set them as HOD.'
        )


class _PersonCreateFormBase(TailwindFormMixin, forms.Form):
    """Shared User-account fields for every "add a person" form."""

    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20, required=False)

    field_order = ['username', 'first_name', 'last_name', 'email', 'phone_number']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def create_user(self, role, is_staff=False, is_superuser=False):
        from django.utils.crypto import get_random_string

        temp_password = get_random_string(10)
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
            phone_number=self.cleaned_data.get('phone_number', ''),
            role=role,
            is_staff=is_staff,
            is_superuser=is_superuser,
            must_change_password=True,
            password=temp_password,
        )
        return user, temp_password


class StudentCreateForm(_PersonCreateFormBase):
    roll_number = forms.CharField(max_length=30)
    program = forms.ModelChoiceField(queryset=None)
    current_semester = forms.ModelChoiceField(queryset=None, required=False)
    admission_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('', '---------')] + StudentProfile.Gender.choices, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    guardian_name = forms.CharField(max_length=150, required=False)
    guardian_phone = forms.CharField(max_length=20, required=False)
    cnic = forms.CharField(max_length=20, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.academics.models import Program, Semester

        self.fields['program'].queryset = Program.objects.filter(is_active=True)
        self.fields['current_semester'].queryset = Semester.objects.select_related('program')

    def clean_roll_number(self):
        roll_number = self.cleaned_data['roll_number']
        if StudentProfile.objects.filter(roll_number=roll_number).exists():
            raise forms.ValidationError('This roll number is already in use.')
        return roll_number

    def save(self):
        user, temp_password = self.create_user(Roles.STUDENT)
        data = self.cleaned_data
        profile = StudentProfile.objects.create(
            user=user,
            roll_number=data['roll_number'],
            program=data['program'],
            current_semester=data.get('current_semester'),
            admission_date=data['admission_date'],
            date_of_birth=data.get('date_of_birth'),
            gender=data.get('gender', ''),
            address=data.get('address', ''),
            guardian_name=data.get('guardian_name', ''),
            guardian_phone=data.get('guardian_phone', ''),
            cnic=data.get('cnic', ''),
        )
        return profile, temp_password


class TeacherCreateForm(_PersonCreateFormBase):
    ROLE_CHOICES = [(Roles.TEACHER, Roles.TEACHER.label), (Roles.HOD, Roles.HOD.label)]

    role = forms.ChoiceField(choices=ROLE_CHOICES)
    employee_id = forms.CharField(max_length=30)
    department = forms.ModelChoiceField(queryset=Department.objects.all())
    designation = forms.CharField(max_length=100, required=False)
    qualification = forms.CharField(max_length=200, required=False)
    joining_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    per_lecture_rate = forms.DecimalField(max_digits=10, decimal_places=2, initial=0)

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        if TeacherProfile.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError('This employee ID is already in use.')
        return employee_id

    def save(self):
        data = self.cleaned_data
        user, temp_password = self.create_user(data['role'])
        profile = TeacherProfile.objects.create(
            user=user,
            employee_id=data['employee_id'],
            department=data['department'],
            designation=data.get('designation', ''),
            qualification=data.get('qualification', ''),
            joining_date=data['joining_date'],
            per_lecture_rate=data['per_lecture_rate'],
        )
        return profile, temp_password


class StaffCreateForm(_PersonCreateFormBase):
    ROLE_CHOICES = [
        (Roles.COORDINATOR, Roles.COORDINATOR.label),
        (Roles.ACCOUNTANT, Roles.ACCOUNTANT.label),
        (Roles.ADMIN, Roles.ADMIN.label),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES)
    employee_id = forms.CharField(max_length=30)
    joining_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        if StaffProfile.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError('This employee ID is already in use.')
        return employee_id

    def save(self):
        data = self.cleaned_data
        role = data['role']
        user, temp_password = self.create_user(
            role, is_staff=True, is_superuser=(role == Roles.ADMIN)
        )
        profile = StaffProfile.objects.create(
            user=user,
            employee_id=data['employee_id'],
            joining_date=data['joining_date'],
            notes=data.get('notes', ''),
        )
        return profile, temp_password


class StudentProfileEditForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['program', 'current_semester', 'status']


class TeacherProfileEditForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['department', 'designation', 'per_lecture_rate', 'employment_status']


class StaffProfileEditForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = ['notes']
