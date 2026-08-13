import { View } from 'react-native';

import { StatCard } from '@/components/ui';

import type { AdminDashboard as AdminDashboardData } from './types';

export function AdminDashboard({ data }: { data: AdminDashboardData }) {
  const entries = Object.entries(data.user_counts);
  return (
    <View className="flex-row flex-wrap gap-3">
      {entries.map(([label, count]) => (
        <View key={label} style={{ width: '47%' }}>
          <StatCard label={label} value={count} />
        </View>
      ))}
    </View>
  );
}
