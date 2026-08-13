// Mirrors apps/reports/api_views.py exactly.

export type AttendanceReportRow = {
  student_id: number;
  roll_number: string;
  name: string;
  delivered: number;
  attended: number;
  absent: number;
  percentage: number | null;
  is_shortage: boolean;
};

export type AttendanceReport = { course_offering: string; rows: AttendanceReportRow[] };

export type AcademicReportRow = {
  student_id: number;
  roll_number: string;
  name: string;
  total_obtained: number;
  total_possible: number;
  percentage: number | null;
  grade_letter: string;
};

export type AcademicReport = { course_offering: string; rows: AcademicReportRow[] };

export type MeritListRow = {
  rank: number;
  student_id: number;
  roll_number: string;
  name: string;
  gpa: number;
  total_credit_hours: number;
};

export type MeritList = { semester: string; rows: MeritListRow[] };

export type StudentBrief = { id: number; roll_number: string; name: string };

export type ProgressCategoryBreakdown = { name: string; obtained: number; possible: number; percentage: number | null };

export type ProgressCourseRow = {
  offering_id: number;
  course: string;
  attendance_percentage: number | null;
  total_obtained: number | null;
  total_possible: number | null;
  grade_letter: string | null;
};

export type ProgressReport = {
  student_id: number;
  roll_number: string;
  name?: string;
  semesters: { id: number; label: string }[];
  selected_semester_id?: number;
  report: {
    semester: string;
    attendance_overall: number | null;
    category_breakdown: ProgressCategoryBreakdown[];
    course_rows: ProgressCourseRow[];
    semester_gpa: number | null;
  } | null;
};
