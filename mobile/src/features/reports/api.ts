import { useQuery } from '@tanstack/react-query';

import { apiFetch, type Paginated } from '@/lib/api/client';

import type { AcademicReport, AttendanceReport, MeritList, ProgressReport, StudentBrief } from './types';

export function useAttendanceReport(offeringId: number | null) {
  return useQuery({
    queryKey: ['reports', 'attendance', offeringId],
    queryFn: () => apiFetch.get<AttendanceReport>('/reports/attendance/', { course_offering: offeringId! }),
    enabled: offeringId !== null,
  });
}

export function useAcademicReport(offeringId: number | null) {
  return useQuery({
    queryKey: ['reports', 'academic', offeringId],
    queryFn: () => apiFetch.get<AcademicReport>('/reports/academic/', { course_offering: offeringId! }),
    enabled: offeringId !== null,
  });
}

export function useMeritList(semesterId: number | null) {
  return useQuery({
    queryKey: ['reports', 'merit-list', semesterId],
    queryFn: () => apiFetch.get<MeritList>('/reports/merit-list/', { semester: semesterId! }),
    enabled: semesterId !== null,
  });
}

export function useProgressStudentSearch(query: string) {
  return useQuery({
    queryKey: ['reports', 'progress-students', query],
    queryFn: () => apiFetch.get<Paginated<StudentBrief>>('/reports/progress-students/', { q: query }),
    select: (data) => data.results,
  });
}

export function useProgressReport(studentId: number, semesterId?: number | null) {
  return useQuery({
    queryKey: ['reports', 'progress', studentId, semesterId],
    queryFn: () => apiFetch.get<ProgressReport>(`/reports/progress/${studentId}/`, semesterId ? { semester: semesterId } : undefined),
  });
}
