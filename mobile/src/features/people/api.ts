import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiFetch, type Paginated } from '@/lib/api/client';

import type { CreatePersonResult, Person } from './types';

export function usePeople(filters: { role?: string; department?: number | string; q?: string } = {}) {
  return useQuery({
    queryKey: ['people', filters],
    queryFn: () => apiFetch.get<Paginated<Person>>('/accounts/people/', filters),
    select: (data) => data.results,
  });
}

export function useToggleActive() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: number) => apiFetch.post<{ id: number; is_active: boolean }>(`/accounts/people/${userId}/toggle-active/`),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['people'] }),
  });
}

function toFormData(fields: Record<string, unknown>, photoUri?: string | null): FormData {
  const form = new FormData();
  for (const [key, value] of Object.entries(fields)) {
    if (value === undefined || value === null || value === '') continue;
    form.append(key, String(value));
  }
  if (photoUri) {
    form.append('photo', { uri: photoUri, name: 'photo.jpg', type: 'image/jpeg' } as unknown as Blob);
  }
  return form;
}

export function useCreatePerson(kind: 'students' | 'teachers' | 'staff') {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ fields, photoUri }: { fields: Record<string, unknown>; photoUri?: string | null }) =>
      apiFetch.postForm<CreatePersonResult>(`/accounts/${kind}/`, toFormData(fields, photoUri)),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['people'] }),
  });
}

export function usePersonProfile<T>(kind: 'students' | 'teachers' | 'staff', profileId: number) {
  return useQuery({
    queryKey: ['people', 'profile', kind, profileId],
    queryFn: () => apiFetch.get<T>(`/accounts/${kind}/${profileId}/`),
  });
}

export function useUpdatePerson(kind: 'students' | 'teachers' | 'staff', profileId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (fields: Record<string, unknown>) =>
      apiFetch.patch<{ id: number }>(`/accounts/${kind}/${profileId}/`, fields),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['people'] });
      void queryClient.invalidateQueries({ queryKey: ['people', 'profile', kind, profileId] });
    },
  });
}
