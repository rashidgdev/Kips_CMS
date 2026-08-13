import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiFetch } from '@/lib/api/client';

import type {
  DayBookEntry,
  DayBookListResponse,
  MonthlyWorkloadSnapshot,
  WorkloadReportResponse,
} from './types';

export function useMyDayBook() {
  return useQuery({
    queryKey: ['daybook', 'mine'],
    queryFn: () => apiFetch.get<DayBookListResponse>('/daybook/mine/'),
  });
}

export function useVerifyQueue() {
  return useQuery({
    queryKey: ['daybook', 'verify-queue'],
    queryFn: () => apiFetch.get<DayBookEntry[]>('/daybook/verify-queue/'),
  });
}

export function useVerifyEntry() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ entryId, remarks }: { entryId: number; remarks: string }) =>
      apiFetch.post<DayBookEntry>(`/daybook/verify/${entryId}/`, { remarks }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['daybook', 'verify-queue'] });
    },
  });
}

/** month format: "YYYY-MM" - matches the web's ?month= query param exactly. */
export function useWorkloadReport(month: string) {
  return useQuery({
    queryKey: ['daybook', 'workload', month],
    queryFn: () => apiFetch.get<WorkloadReportResponse>('/daybook/workload/', { month }),
  });
}

export function useGenerateWorkloadSnapshot(month: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      apiFetch.post<{ year: number; month: number; generated_count: number; snapshots: MonthlyWorkloadSnapshot[] }>(
        `/daybook/workload/generate/?month=${encodeURIComponent(month)}`,
      ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['daybook', 'workload', month] });
    },
  });
}
