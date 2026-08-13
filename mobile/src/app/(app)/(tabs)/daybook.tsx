import { FlatList, RefreshControl, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Card, EmptyState, ErrorState, LoadingState, StatCard } from '@/components/ui';
import { useMyDayBook } from '@/features/daybook/api';
import { formatCurrency } from '@/lib/format';

export default function DayBookScreen() {
  const { data, isPending, isError, error, refetch, isRefetching } = useMyDayBook();

  if (isPending) return <LoadingState />;
  if (isError) return <ErrorState error={error} onRetry={() => void refetch()} />;

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      <FlatList
        data={data.entries}
        keyExtractor={(item) => String(item.id)}
        contentContainerClassName="px-4 py-4 gap-2"
        refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={() => void refetch()} />}
        ListHeaderComponent={
          <View className="mb-4 gap-3">
            <Text className="text-xs text-gray-500">This month</Text>
            <View className="flex-row gap-3">
              <StatCard label="Total Lectures" value={data.workload.total_lectures} />
              <StatCard label="Verified" value={data.workload.verified_lectures} tone="success" />
            </View>
            <View className="flex-row gap-3">
              <StatCard label="Unverified" value={data.workload.unverified_lectures} tone="danger" />
              <StatCard label="Estimated Pay" value={formatCurrency(data.workload.total_amount)} />
            </View>
          </View>
        }
        ListEmptyComponent={<EmptyState title="No lectures recorded yet" />}
        renderItem={({ item }) => (
          <Card>
            <View className="flex-row items-center justify-between">
              <Text className="flex-1 text-sm font-semibold text-gray-900">{item.course}</Text>
              <Badge label={item.is_verified ? 'Verified' : 'Pending'} tone={item.is_verified ? 'success' : 'warning'} />
            </View>
            <Text className="mt-0.5 text-xs text-gray-500">
              {item.session_date}
              {item.topic_covered ? ` · ${item.topic_covered}` : ''}
            </Text>
            {item.is_verified && item.verified_by_name && (
              <Text className="mt-1 text-xs text-gray-400">Verified by {item.verified_by_name}</Text>
            )}
          </Card>
        )}
      />
    </SafeAreaView>
  );
}
