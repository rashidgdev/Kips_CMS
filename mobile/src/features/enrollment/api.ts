import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiFetch } from '@/lib/api/client';

type OfferingCandidates = {
  offering: { id: number; course_label: string; semester_label: string };
  students: { id: number; roll_number: string; name: string; already_enrolled: boolean }[];
};

type StudentCandidates = {
  student: { id: number; roll_number: string; name: string };
  offerings: { id: number; course: string; semester: string; already_enrolled: boolean }[];
};

export function useOfferingCandidates(offeringId: number | null) {
  return useQuery({
    queryKey: ['enrollment', 'by-offering', offeringId],
    queryFn: () => apiFetch.get<OfferingCandidates>('/academics/enroll-by-offering/', { offering: offeringId! }),
    enabled: offeringId !== null,
  });
}

export function useEnrollByOffering() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ offeringId, studentIds }: { offeringId: number; studentIds: number[] }) =>
      apiFetch.post<{ enrolled_count: number }>('/academics/enroll-by-offering/', {
        offering: offeringId,
        student_ids: studentIds,
      }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ['enrollment', 'by-offering', variables.offeringId] });
    },
  });
}

export function useStudentCandidates(studentId: number | null) {
  return useQuery({
    queryKey: ['enrollment', 'by-student', studentId],
    queryFn: () => apiFetch.get<StudentCandidates>('/academics/enroll-by-student/', { student: studentId! }),
    enabled: studentId !== null,
  });
}

export function useEnrollByStudent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, offeringIds }: { studentId: number; offeringIds: number[] }) =>
      apiFetch.post<{ enrolled_count: number }>('/academics/enroll-by-student/', {
        student: studentId,
        offering_ids: offeringIds,
      }),
    onSuccess: (_data, variables) => {
      void queryClient.invalidateQueries({ queryKey: ['enrollment', 'by-student', variables.studentId] });
    },
  });
}
