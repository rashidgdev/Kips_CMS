import { router, Stack, useLocalSearchParams } from 'expo-router';
import { FlatList, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Button, Card, EmptyState, ErrorState, LoadingState, StatCard } from '@/components/ui';
import { useGenerateFeeItems, useStudentFeeDetail } from '@/features/finance/api';
import { formatCurrency } from '@/lib/format';

const STATUS_TONE = { paid: 'success', partial: 'warning', overdue: 'danger', unpaid: 'neutral' } as const;
const CHALLAN_STATUS_TONE = { paid: 'success', overdue: 'danger', unpaid: 'neutral', cancelled: 'neutral' } as const;

export default function StudentFeeDetailScreen() {
  const { studentId } = useLocalSearchParams<{ studentId: string }>();
  const id = Number(studentId);
  const { data, isPending, isError, error, refetch } = useStudentFeeDetail(id);
  const generateItems = useGenerateFeeItems(id);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: data ? `Roll No. ${data.roll_number}` : 'Student Fees' }} />
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data.overview.rows}
          keyExtractor={(row) => String(row.item.id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListHeaderComponent={
            <View className="mb-4 gap-3">
              <View className="flex-row gap-3">
                <StatCard label="Total Due" value={formatCurrency(data.overview.total_due)} />
                <StatCard label="Outstanding" value={formatCurrency(data.overview.total_outstanding)} tone="danger" />
              </View>

              <Button
                label="Generate This Semester's Fee Items"
                variant="secondary"
                loading={generateItems.isPending}
                onPress={() => generateItems.mutate()}
              />
              {generateItems.isError && (
                <Text className="text-xs text-red-600">{generateItems.error.message}</Text>
              )}
              {generateItems.isSuccess && (
                <Text className="text-xs text-green-700">
                  {generateItems.data.created_count > 0
                    ? `Generated ${generateItems.data.created_count} new fee item(s).`
                    : 'Fee items already up to date.'}
                </Text>
              )}

              <Button
                label="Generate Challan"
                onPress={() =>
                  router.push({ pathname: '/finance/challan-generate/[studentId]', params: { studentId: String(id) } })
                }
              />

              {data.challans.length > 0 && (
                <View className="mt-2">
                  <Text className="mb-2 text-base font-semibold text-gray-900">Challans</Text>
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
                        <Text className="mt-1 text-xs text-gray-500">{formatCurrency(challan.total_amount)}</Text>
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
            <Card
              onPress={
                row.outstanding > 0
                  ? () =>
                      router.push({
                        pathname: '/finance/pay/[itemId]',
                        params: { itemId: String(row.item.id), studentId: String(id) },
                      })
                  : undefined
              }
            >
              <View className="flex-row items-center justify-between">
                <Text className="flex-1 text-sm font-semibold text-gray-900">{row.item.category_label}</Text>
                <Badge label={row.status} tone={STATUS_TONE[row.status]} />
              </View>
              <Text className="mt-1 text-xs text-gray-500">{row.item.semester_label}</Text>
              <Text className="mt-1 text-xs text-gray-600">
                {formatCurrency(row.paid)} paid of {formatCurrency(row.item.amount_due)}
                {row.outstanding > 0 ? ' · Tap to record a payment' : ''}
              </Text>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
