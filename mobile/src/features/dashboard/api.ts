import { useQuery } from '@tanstack/react-query';

import { apiFetch } from '@/lib/api/client';

import type { DashboardData } from './types';

export function useDashboard() {
  return useQuery({
    queryKey: ['dashboard', 'me'],
    queryFn: () => apiFetch.get<DashboardData>('/dashboard/me/'),
  });
}
