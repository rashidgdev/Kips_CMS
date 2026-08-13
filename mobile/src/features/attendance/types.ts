// Mirrors apps/attendance/api_views.py + serializers.py exactly.

export type TeacherOffering = { id: number; course: string; semester: string; section: string };

export type LectureSession = {
  id: number;
  course_offering: number;
  course_offering_label: string;
  date: string;
  start_time: string;
  end_time: string;
  topic_covered: string;
};

export type AttendanceStatus = 'present' | 'absent' | 'leave' | 'late';

export type RosterRow = {
  student_id: number;
  roll_number: string;
  name: string;
  status: AttendanceStatus;
};

export type RosterResponse = {
  session: LectureSession;
  status_choices: [AttendanceStatus, string][];
  rows: RosterRow[];
};

export type StudentAttendanceOverviewRow = {
  course_offering_id: number;
  course: string;
  delivered: number;
  attended: number;
  absent: number;
  percentage: number | null;
  threshold: number;
  is_shortage: boolean;
};

export type StudentCourseAttendanceDetail = {
  course: string;
  delivered: number;
  attended: number;
  absent: number;
  percentage: number | null;
  is_shortage: boolean;
  records: { session_id: number; date: string; status: AttendanceStatus }[];
};
