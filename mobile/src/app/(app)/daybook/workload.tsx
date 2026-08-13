import { Stack } from 'expo-router';
import { useState } from 'react';
import { FlatList, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Button, Card, EmptyState, ErrorState, LoadingState, StatCard } from '@/components/ui';
import { useGenerateWorkloadSnapshot, useWorkloadReport } from '@/features/daybook/api';
import { formatCurrency } from '@/lib/format';

function currentMonth() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

export default function WorkloadReportScreen() {
  const [month] = useState(currentMonth());
  const { data, isPending, isError, error, refetch } = useWorkloadReport(month);
  const generateSnapshot = useGenerateWorkloadSnapshot(month);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: `Workload · ${month}` }} />
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data.rows}
          keyExtractor={(item) => String(item.teacher_id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListHeaderComponent={
            <View className="mb-4 gap-3">
              <StatCard label="Total Payroll" value={formatCurrency(data.total_amount)} />
              <Button
                label={data.snapshot_generated ? 'Regenerate Payroll Snapshot' : 'Generate Payroll Snapshot'}
                variant="secondary"
                loading={generateSnapshot.isPending}
                onPress={() => generateSnapshot.mutate()}
              />
              {generateSnapshot.isSuccess && (
                <Text className="text-xs text-green-700">
                  Snapshot generated for {generateSnapshot.data.generated_count} teacher(s).
                </Text>
              )}
              {generateSnapshot.isError && (
                <Text className="text-xs text-red-600">{generateSnapshot.error.message}</Text>
              )}
            </View>
          }
          ListEmptyComponent={<EmptyState title="No teacher workload data" />}
          renderItem={({ item }) => (
            <Card>
              <View className="flex-row items-center justify-between">
                <Text className="flex-1 text-sm font-semibold text-gray-900">{item.teacher_name}</Text>
                <Badge label={item.department} tone="brand" />
              </View>
              <Text className="mt-0.5 text-xs text-gray-500">{item.employee_id}</Text>
              <Text className="mt-1 text-xs text-gray-600">
                {item.verified_lectures}/{item.total_lectures} lectures verified · {formatCurrency(item.total_amount)}
              </Text>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
