// Mirrors apps/dashboard/api_views.py::dashboard_me's payload shape exactly, per role.

export type StudentDashboard = {
  role: 'student';
  enrollments: { id: number; course: string; teacher: string; status: string }[];
  cgpa: number | null;
  current_semester_gpa: number | null;
  overall_attendance_percent: number | null;
};

export type TeacherDashboard = {
  role: 'teacher' | 'hod';
  offerings: { id: number; course: string; semester: string; section: string }[];
  todays_classes: { id: number; course: string; room: string; start_time: string; end_time: string }[];
  department?: string | null; // hod only
};

export type CoordinatorDashboard = {
  role: 'coordinator';
  program_count: number;
  offering_count: number;
};

export type AccountantDashboard = {
  role: 'accountant';
  student_count: number;
  total_due: number;
  total_paid: number;
  total_outstanding: number;
};

export type AdminDashboard = {
  role: 'admin';
  user_counts: Record<string, number>;
};

export type DashboardData =
  | StudentDashboard
  | TeacherDashboard
  | CoordinatorDashboard
  | AccountantDashboard
  | AdminDashboard;
