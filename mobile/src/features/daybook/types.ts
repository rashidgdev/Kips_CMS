// Mirrors apps/daybook/api_views.py + serializers.py exactly.

export type DayBookEntry = {
  id: number;
  session: number;
  course: string;
  teacher: string;
  session_date: string;
  topic_covered: string;
  verified_by_name: string | null;
  verified_at: string | null;
  remarks: string;
  is_verified: boolean;
};

export type TeacherWorkload = {
  total_lectures: number;
  verified_lectures: number;
  unverified_lectures: number;
  per_lecture_rate: number;
  total_amount: number;
};

export type DayBookListResponse = {
  entries: DayBookEntry[];
  workload: TeacherWorkload;
};

export type WorkloadReportRow = {
  teacher_id: number;
  employee_id: string;
  teacher_name: string;
  department: string;
  total_lectures: number;
  verified_lectures: number;
  unverified_lectures: number;
  per_lecture_rate: number;
  total_amount: number;
};

export type WorkloadReportResponse = {
  year: number;
  month: number;
  total_amount: number;
  snapshot_generated: boolean;
  rows: WorkloadReportRow[];
};

export type MonthlyWorkloadSnapshot = {
  id: number;
  teacher: number;
  teacher_name: string;
  employee_id: string;
  year: number;
  month: number;
  total_lectures: number;
  verified_lectures: number;
  per_lecture_rate: number;
  total_amount: number;
};
