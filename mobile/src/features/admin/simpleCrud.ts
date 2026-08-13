import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiFetch, type Paginated } from '@/lib/api/client';

/**
 * Generic hooks for the nine "setup/reference data" resources that are all
 * plain RoleScopedModelViewSet CRUD with the same DRF pagination shape
 * (Program, Semester, Course, CourseOffering, Room, TimeSlot,
 * AssessmentCategory, FeeCategory, FeeStructure) - avoids re-writing the
 * same list/create/update/delete plumbing nine times. Each resource's own
 * screen file only needs to describe its fields (see SimpleCrudScreen.tsx).
 */
export function useSimpleCrudList<T>(basePath: string) {
  return useQuery({
    queryKey: ['admin', basePath],
    queryFn: () => apiFetch.get<Paginated<T>>(basePath),
  });
}

export function useSimpleCrudCreate<T>(basePath: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) => apiFetch.post<T>(basePath, body),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['admin', basePath] }),
  });
}

export function useSimpleCrudUpdate<T>(basePath: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Record<string, unknown> }) =>
      apiFetch.patch<T>(`${basePath}${id}/`, body),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['admin', basePath] }),
  });
}

export function useSimpleCrudDelete(basePath: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => apiFetch.delete(`${basePath}${id}/`),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['admin', basePath] }),
  });
}
