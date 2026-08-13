// Mirrors apps/assessments/api_views.py + serializers.py exactly.

export type TeacherOffering = { id: number; course: string; semester: string; section: string };

export type AssessmentCategory = { id: number; name: string; default_weight_percent: number };

export type Assessment = {
  id: number;
  course_offering: number;
  category: number;
  category_label: string;
  title: string;
  total_marks: number;
  weight_percent: number;
  date: string;
};

export type MarksRosterRow = {
  student_id: number;
  roll_number: string;
  name: string;
  obtained_marks: number | null;
};

export type MarksRosterResponse = {
  assessment: Assessment;
  rows: MarksRosterRow[];
};

export type StudentGradeResult = {
  course_offering_id: number;
  course: string;
  semester: string;
  total_obtained: number;
  total_possible: number;
  percentage: number | null;
  grade_letter: string;
};

export type StudentGradesOverview = {
  results: StudentGradeResult[];
  current_semester_gpa: number | null;
  cgpa: number | null;
};

export type StudentCourseGradeDetail = {
  course: string;
  total_obtained: number | null;
  total_possible: number | null;
  percentage: number | null;
  grade_letter: string | null;
  marks: {
    assessment_id: number;
    title: string;
    category: string;
    obtained_marks: number;
    total_marks: number;
  }[];
};
