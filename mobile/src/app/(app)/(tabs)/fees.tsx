import { router } from 'expo-router';
import { FlatList, RefreshControl, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Card, EmptyState, ErrorState, LoadingState, StatCard } from '@/components/ui';
import { useMyFeeOverview } from '@/features/finance/api';
import { formatCurrency } from '@/lib/format';

const STATUS_TONE = { paid: 'success', partial: 'warning', overdue: 'danger', unpaid: 'neutral' } as const;
const CHALLAN_STATUS_TONE = { paid: 'success', overdue: 'danger', unpaid: 'neutral', cancelled: 'neutral' } as const;

export default function FeesScreen() {
  const { data, isPending, isError, error, refetch, isRefetching } = useMyFeeOverview();

  if (isPending) return <LoadingState />;
  if (isError) return <ErrorState error={error} onRetry={() => void refetch()} />;

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      <FlatList
        data={data.overview.rows}
        keyExtractor={(row) => String(row.item.id)}
        contentContainerClassName="px-4 py-4 gap-2"
        refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={() => void refetch()} />}
        ListHeaderComponent={
          <View className="mb-4 gap-3">
            <View className="flex-row gap-3">
              <StatCard label="Total Due" value={formatCurrency(data.overview.total_due)} />
              <StatCard label="Paid" value={formatCurrency(data.overview.total_paid)} tone="success" />
            </View>
            <StatCard label="Outstanding" value={formatCurrency(data.overview.total_outstanding)} tone="danger" />

            {data.challans.length > 0 && (
              <View className="mt-2">
                <Text className="mb-2 text-base font-semibold text-gray-900">My Challans</Text>
                <View className="gap-2">
                  {data.challans.map((challan) => (
                    <Card
                      key={challan.id}
                      onPress={() =>
                        router.push({ pathname: '/challans/[challanId]', params: { challanId: String(challan.id) } })
                      }
                    >
                      <View className="flex-row items-center justify-between">
                        <Text className="text-sm font-semibold text-gray-900">{challan.challan_number}</Text>
                        <Badge label={challan.status} tone={CHALLAN_STATUS_TONE[challan.status]} />
                      </View>
                      <Text className="mt-1 text-xs text-gray-500">
                        {formatCurrency(challan.total_amount)} · Due {challan.due_date}
                      </Text>
                    </Card>
                  ))}
                </View>
              </View>
            )}

            <Text className="mt-2 text-base font-semibold text-gray-900">Fee Items</Text>
          </View>
        }
        ListEmptyComponent={<EmptyState title="No fee items yet" />}
        renderItem={({ item: row }) => (
          <Card>
            <View className="flex-row items-center justify-between">
              <Text className="flex-1 text-sm font-semibold text-gray-900">{row.item.category_label}</Text>
              <Badge label={row.status} tone={STATUS_TONE[row.status]} />
            </View>
            <Text className="mt-1 text-xs text-gray-500">
              {row.item.semester_label} · Due {row.item.due_date}
            </Text>
            <Text className="mt-1 text-xs text-gray-600">
              {formatCurrency(row.paid)} paid of {formatCurrency(row.item.amount_due)}
            </Text>
          </Card>
        )}
      />
    </SafeAreaView>
  );
}
