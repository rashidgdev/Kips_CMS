import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { ApiError, apiFetch } from '@/lib/api/client';

import type {
  Assessment,
  AssessmentCategory,
  MarksRosterResponse,
  StudentCourseGradeDetail,
  StudentGradesOverview,
  TeacherOffering,
} from './types';

export function useTeacherOfferings() {
  return useQuery({
    queryKey: ['assessments', 'offerings'],
    queryFn: () => apiFetch.get<TeacherOffering[]>('/assessments/offerings/'),
  });
}

export function useCategoryOptions() {
  return useQuery({
    queryKey: ['assessments', 'category-options'],
    queryFn: () => apiFetch.get<AssessmentCategory[]>('/assessments/category-options/'),
  });
}

export function useAssessments(offeringId: number) {
  return useQuery({
    queryKey: ['assessments', 'list', offeringId],
    queryFn: () => apiFetch.get<Assessment[]>(`/assessments/offerings/${offeringId}/assessments/`),
  });
}

export function useCreateAssessment(offeringId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { category: number; title: string; total_marks: number; weight_percent: number; date: string }) =>
      apiFetch.post<Assessment>(`/assessments/offerings/${offeringId}/assessments/`, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['assessments', 'list', offeringId] });
    },
  });
}

export function useMarksRoster(assessmentId: number) {
  return useQuery({
    queryKey: ['assessments', 'marks', assessmentId],
    queryFn: () => apiFetch.get<MarksRosterResponse>(`/assessments/assessments/${assessmentId}/marks/`),
  });
}

/** Partial-success bulk save: throws ApiError with `.data.errors: string[]` if any row failed - valid rows still saved server-side. */
export function useSaveMarks(assessmentId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (marks: Record<number, string>) =>
      apiFetch.post<{ detail: string }>(`/assessments/assessments/${assessmentId}/marks/`, { marks }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['assessments', 'marks', assessmentId] });
    },
  });
}

export function extractMarksErrors(error: unknown): string[] {
  if (error instanceof ApiError && error.data && typeof error.data === 'object' && 'errors' in error.data) {
    const errors = (error.data as { errors: unknown }).errors;
    if (Array.isArray(errors)) return errors.filter((e): e is string => typeof e === 'string');
  }
  return [];
}

export function useStudentGradesOverview() {
  return useQuery({
    queryKey: ['assessments', 'my'],
    queryFn: () => apiFetch.get<StudentGradesOverview>('/assessments/my/'),
  });
}

export function useStudentCourseGrades(offeringId: number) {
  return useQuery({
    queryKey: ['assessments', 'my', offeringId],
    queryFn: () => apiFetch.get<StudentCourseGradeDetail>(`/assessments/my/${offeringId}/`),
  });
}
