import { Stack, useLocalSearchParams } from 'expo-router';
import { FlatList, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Card, EmptyState, ErrorState, LoadingState, StatCard } from '@/components/ui';
import { useStudentCourseAttendance } from '@/features/attendance/api';
import { formatPercent } from '@/lib/format';

const STATUS_TONE = { present: 'success', absent: 'danger', leave: 'warning', late: 'brand' } as const;

export default function StudentCourseAttendanceScreen() {
  const { offeringId } = useLocalSearchParams<{ offeringId: string }>();
  const id = Number(offeringId);
  const { data, isPending, isError, error, refetch } = useStudentCourseAttendance(id);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: data?.course ?? 'Attendance' }} />
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data.records}
          keyExtractor={(item) => String(item.session_id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListHeaderComponent={
            <View className="mb-4 gap-3">
              <View className="flex-row gap-3">
                <StatCard label="Attended" value={`${data.attended}/${data.delivered}`} />
                <StatCard
                  label="Percentage"
                  value={formatPercent(data.percentage)}
                  tone={data.is_shortage ? 'danger' : 'success'}
                />
              </View>
              {data.is_shortage && (
                <Card className="border-red-200 bg-red-50">
                  <Text className="text-sm font-medium text-red-700">
                    Your attendance in this course is below the required threshold.
                  </Text>
                </Card>
              )}
            </View>
          }
          ListEmptyComponent={<EmptyState title="No lectures recorded yet" />}
          renderItem={({ item }) => (
            <Card className="flex-row items-center justify-between">
              <Text className="text-sm text-gray-900">{item.date}</Text>
              <Badge label={item.status} tone={STATUS_TONE[item.status]} />
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
