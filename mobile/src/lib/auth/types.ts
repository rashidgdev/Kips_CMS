// Mirrors apps/accounts/models/user.py::Roles exactly.
export type Role = 'student' | 'teacher' | 'hod' | 'coordinator' | 'accountant' | 'admin';

export type StudentProfileSummary = {
  id: number;
  roll_number: string;
  program_id: number | null;
  program: string | null;
  current_semester_id: number | null;
  current_semester: string | null;
  status: string;
};

export type TeacherProfileSummary = {
  id: number;
  employee_id: string;
  department_id: number | null;
  department: string | null;
  designation: string;
  employment_status: string;
};

export type StaffProfileSummary = {
  id: number;
  employee_id: string;
};

// Matches apps/accounts/api_views.py::me exactly.
export type Me = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone_number: string;
  role: Role;
  role_display: string;
  is_superuser: boolean;
  must_change_password: boolean;
  photo_url: string | null;
  profile: StudentProfileSummary | TeacherProfileSummary | StaffProfileSummary | null;
};

export type TokenPair = {
  access: string;
  refresh: string;
};
