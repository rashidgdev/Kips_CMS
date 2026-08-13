import { router } from 'expo-router';
import { FlatList, RefreshControl, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Card, EmptyState, ErrorState, LoadingState } from '@/components/ui';
import { useChallanList } from '@/features/finance/api';
import { formatCurrency } from '@/lib/format';

const STATUS_TONE = { paid: 'success', overdue: 'danger', unpaid: 'neutral', cancelled: 'neutral' } as const;

export default function ChallansScreen() {
  const { data, isPending, isError, error, refetch, isRefetching } = useChallanList();

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data}
          keyExtractor={(item) => String(item.id)}
          contentContainerClassName="px-4 py-4 gap-2"
          refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={() => void refetch()} />}
          ListEmptyComponent={<EmptyState title="No challans issued yet" />}
          renderItem={({ item }) => (
            <Card
              onPress={() =>
                router.push({ pathname: '/challans/[challanId]', params: { challanId: String(item.id) } })
              }
            >
              <View className="flex-row items-center justify-between">
                <Text className="text-sm font-semibold text-gray-900">{item.challan_number}</Text>
                <Badge label={item.status} tone={STATUS_TONE[item.status]} />
              </View>
              <Text className="mt-1 text-xs text-gray-500">{item.student_label}</Text>
              <Text className="mt-1 text-xs text-gray-600">
                {formatCurrency(item.total_amount)} · Due {item.due_date}
              </Text>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
