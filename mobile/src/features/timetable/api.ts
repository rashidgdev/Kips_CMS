import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiFetch, type Paginated } from '@/lib/api/client';

import type {
  CourseOfferingOption,
  MyGridResponse,
  Room,
  SemesterGridResponse,
  SemesterOption,
  TimeSlot,
  TimetableEntry,
} from './types';

export function useSemesters() {
  return useQuery({
    queryKey: ['timetable', 'semesters'],
    queryFn: () => apiFetch.get<SemesterOption[]>('/timetable/semesters/'),
  });
}

export function useSemesterGrid(semesterId: number | null) {
  return useQuery({
    queryKey: ['timetable', 'grid', semesterId],
    queryFn: () =>
      apiFetch.get<SemesterGridResponse>(semesterId ? `/timetable/grid/${semesterId}/` : '/timetable/grid/'),
  });
}

export function useTeacherGrid() {
  return useQuery({
    queryKey: ['timetable', 'mine', 'teacher'],
    queryFn: () => apiFetch.get<MyGridResponse>('/timetable/mine/teacher/'),
  });
}

export function useStudentGrid() {
  return useQuery({
    queryKey: ['timetable', 'mine', 'student'],
    queryFn: () => apiFetch.get<MyGridResponse>('/timetable/mine/student/'),
  });
}

export function useRooms() {
  return useQuery({
    queryKey: ['timetable', 'rooms'],
    queryFn: () => apiFetch.get<Paginated<Room>>('/timetable/rooms/'),
  });
}

export function useTimeSlots() {
  return useQuery({
    queryKey: ['timetable', 'timeslots'],
    queryFn: () => apiFetch.get<Paginated<TimeSlot>>('/timetable/timeslots/'),
  });
}

export function useOfferingsForSemester(semesterId: number | null) {
  return useQuery({
    queryKey: ['academics', 'offerings', semesterId],
    queryFn: () => apiFetch.get<Paginated<CourseOfferingOption>>('/academics/offerings/'),
    select: (data) => (semesterId ? data.results.filter((o) => o.semester === semesterId) : data.results),
    enabled: semesterId !== null,
  });
}

export function useScheduleEntry(semesterId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { course_offering: number; room: number; time_slot: number }) =>
      apiFetch.post<TimetableEntry>(`/timetable/grid/${semesterId}/schedule/`, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['timetable', 'grid', semesterId] });
    },
  });
}

export function useUnscheduleEntry(semesterId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (entryId: number) => apiFetch.delete(`/timetable/entries/${entryId}/`),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['timetable', 'grid', semesterId] });
    },
  });
}
