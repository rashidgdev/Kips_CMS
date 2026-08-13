import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiFetch } from '@/lib/api/client';

import type {
  LectureSession,
  RosterResponse,
  StudentAttendanceOverviewRow,
  StudentCourseAttendanceDetail,
  TeacherOffering,
} from './types';

export function useTeacherOfferings() {
  return useQuery({
    queryKey: ['attendance', 'offerings'],
    queryFn: () => apiFetch.get<TeacherOffering[]>('/attendance/offerings/'),
  });
}

export function useSessions(offeringId: number) {
  return useQuery({
    queryKey: ['attendance', 'sessions', offeringId],
    queryFn: () => apiFetch.get<LectureSession[]>(`/attendance/offerings/${offeringId}/sessions/`),
  });
}

export function useCreateSession(offeringId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { date: string; start_time: string; end_time: string; topic_covered: string }) =>
      apiFetch.post<LectureSession>(`/attendance/offerings/${offeringId}/sessions/`, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['attendance', 'sessions', offeringId] });
    },
  });
}

export function useRoster(sessionId: number) {
  return useQuery({
    queryKey: ['attendance', 'roster', sessionId],
    queryFn: () => apiFetch.get<RosterResponse>(`/attendance/sessions/${sessionId}/mark/`),
  });
}

export function useMarkAttendance(sessionId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (statuses: Record<number, string>) =>
      apiFetch.post<{ detail: string; saved_count: number }>(`/attendance/sessions/${sessionId}/mark/`, {
        statuses,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['attendance', 'roster', sessionId] });
    },
  });
}

export function useStudentAttendanceOverview() {
  return useQuery({
    queryKey: ['attendance', 'my'],
    queryFn: () => apiFetch.get<StudentAttendanceOverviewRow[]>('/attendance/my/'),
  });
}

export function useStudentCourseAttendance(offeringId: number) {
  return useQuery({
    queryKey: ['attendance', 'my', offeringId],
    queryFn: () => apiFetch.get<StudentCourseAttendanceDetail>(`/attendance/my/${offeringId}/`),
  });
}
