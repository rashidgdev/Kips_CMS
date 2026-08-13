import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiFetch } from '@/lib/api/client';

import type {
  Challan,
  ChallanDetail,
  ChallanGenerateOptions,
  MyFeeOverview,
  Payment,
  StudentFeeDetail,
  StudentFeeItem,
  StudentFeeSummaryRow,
} from './types';

export function useMyFeeOverview() {
  return useQuery({
    queryKey: ['finance', 'my'],
    queryFn: () => apiFetch.get<MyFeeOverview>('/finance/my/'),
  });
}

export function useStudentFeeSummary() {
  return useQuery({
    queryKey: ['finance', 'students'],
    queryFn: () => apiFetch.get<StudentFeeSummaryRow[]>('/finance/students/'),
  });
}

export function useStudentFeeDetail(studentId: number) {
  return useQuery({
    queryKey: ['finance', 'student', studentId],
    queryFn: () => apiFetch.get<StudentFeeDetail>(`/finance/students/${studentId}/`),
  });
}

export function useGenerateFeeItems(studentId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () =>
      apiFetch.post<{ created: unknown[]; created_count: number }>(`/finance/students/${studentId}/generate/`),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['finance', 'student', studentId] });
    },
  });
}

export function useRecordPayment(itemId: number, studentId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { amount_paid: string; payment_date: string; payment_method: string }) =>
      apiFetch.post<Payment>(`/finance/items/${itemId}/pay/`, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['finance', 'student', studentId] });
    },
  });
}

export function useChallanGenerateOptions(studentId: number) {
  return useQuery({
    queryKey: ['finance', 'challan-generate', studentId],
    queryFn: () => apiFetch.get<ChallanGenerateOptions>(`/finance/students/${studentId}/generate-challan/`),
  });
}

export function useGenerateChallan(studentId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (items: { fee_item_id: number; amount: string }[]) =>
      apiFetch.post<{ challan: Challan; reused_existing: boolean }>(
        `/finance/students/${studentId}/generate-challan/`,
        { items },
      ),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['finance', 'student', studentId] });
      void queryClient.invalidateQueries({ queryKey: ['finance', 'challans'] });
    },
  });
}

export function useChallanList() {
  return useQuery({
    queryKey: ['finance', 'challans'],
    queryFn: () => apiFetch.get<Challan[]>('/finance/challans/'),
  });
}

export function useChallanDetail(challanId: number) {
  return useQuery({
    queryKey: ['finance', 'challan', challanId],
    queryFn: () => apiFetch.get<ChallanDetail>(`/finance/challans/${challanId}/`),
  });
}

export function useRecordChallanPayment(challanId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: { payment_date: string; payment_method: string }) =>
      apiFetch.post<{ payments: Payment[] }>(`/finance/challans/${challanId}/pay/`, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['finance', 'challan', challanId] });
      void queryClient.invalidateQueries({ queryKey: ['finance', 'challans'] });
    },
  });
}

export function useCancelChallan(challanId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiFetch.post<Challan>(`/finance/challans/${challanId}/cancel/`),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['finance', 'challan', challanId] });
      void queryClient.invalidateQueries({ queryKey: ['finance', 'challans'] });
    },
  });
}

export type { StudentFeeItem };
