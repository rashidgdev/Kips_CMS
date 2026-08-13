import { View } from 'react-native';

import { StatCard } from '@/components/ui';
import { formatCurrency } from '@/lib/format';

import type { AccountantDashboard as AccountantDashboardData } from './types';

export function AccountantDashboard({ data }: { data: AccountantDashboardData }) {
  return (
    <View className="gap-3">
      <View className="flex-row gap-3">
        <StatCard label="Students" value={data.student_count} />
        <StatCard label="Total Due" value={formatCurrency(data.total_due)} />
      </View>
      <View className="flex-row gap-3">
        <StatCard label="Total Paid" value={formatCurrency(data.total_paid)} tone="success" />
        <StatCard label="Outstanding" value={formatCurrency(data.total_outstanding)} tone="danger" />
      </View>
    </View>
  );
}
