import { View } from 'react-native';

import { StatCard } from '@/components/ui';

import type { CoordinatorDashboard as CoordinatorDashboardData } from './types';

export function CoordinatorDashboard({ data }: { data: CoordinatorDashboardData }) {
  return (
    <View className="flex-row gap-3">
      <StatCard label="Active Programs" value={data.program_count} />
      <StatCard label="Active Offerings" value={data.offering_count} />
    </View>
  );
}
