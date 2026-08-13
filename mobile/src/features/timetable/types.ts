// Mirrors apps/timetable/api_views.py's _serialize_grid()/serializers.py exactly.

export type GridDay = { value: number; label: string };

export type GridCell = {
  day: number;
  day_label: string;
  entry_id: number | null;
  course: string | null;
  teacher: string | null;
  room: string | null;
};

export type GridRow =
  | { type: 'period'; start_time: string; end_time: string; label: string; cells: GridCell[] }
  | { type: 'break'; start_time: string; end_time: string; duration_minutes: number };

export type Grid = { days: GridDay[]; rows: GridRow[] };

export type SemesterGridResponse = {
  semester: { id: number; name: string } | null;
  grid: Grid;
  pdf_url: string | null;
};

export type MyGridResponse = { grid: Grid; pdf_url: string };

export type SemesterOption = { id: number; name: string; is_current: boolean };

export type Room = { id: number; name: string; building: string; capacity: number; room_type: string };

export type TimeSlot = {
  id: number;
  day_of_week: number;
  day_of_week_display: string;
  start_time: string;
  start_time_display: string;
  end_time: string;
  end_time_display: string;
  label: string;
};

export type TimetableEntry = {
  id: number;
  course_offering: number;
  course: string;
  teacher: string;
  room: number;
  room_name: string;
  time_slot: number;
  time_slot_label: string;
};

export type CourseOfferingOption = {
  id: number;
  course_label: string;
  semester: number;
  semester_label: string;
  teacher_label: string;
  section: string;
};
