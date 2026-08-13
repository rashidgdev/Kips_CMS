import { router } from 'expo-router';
import { FlatList, RefreshControl, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Card, EmptyState, ErrorState, LoadingState, StatCard } from '@/components/ui';
import { useStudentGradesOverview } from '@/features/assessments/api';
import { formatPercent } from '@/lib/format';

const GRADE_TONE: Record<string, 'success' | 'warning' | 'danger'> = { F: 'danger' };

export default function GradesScreen() {
  const { data, isPending, isError, error, refetch, isRefetching } = useStudentGradesOverview();

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data.results}
          keyExtractor={(item) => String(item.course_offering_id)}
          contentContainerClassName="px-4 py-4 gap-2"
          refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={() => void refetch()} />}
          ListHeaderComponent={
            <View className="mb-4 flex-row gap-3">
              <StatCard label="CGPA" value={data.cgpa?.toFixed(2) ?? '—'} />
              <StatCard label="Semester GPA" value={data.current_semester_gpa?.toFixed(2) ?? '—'} />
            </View>
          }
          ListEmptyComponent={<EmptyState title="No graded courses yet" />}
          renderItem={({ item }) => (
            <Card
              onPress={() =>
                router.push({ pathname: '/grades/[offeringId]', params: { offeringId: String(item.course_offering_id) } })
              }
            >
              <View className="flex-row items-center justify-between">
                <Text className="flex-1 text-sm font-semibold text-gray-900">{item.course}</Text>
                {item.grade_letter ? (
                  <Badge label={item.grade_letter} tone={GRADE_TONE[item.grade_letter] ?? 'brand'} />
                ) : (
                  <Badge label="Not graded" tone="neutral" />
                )}
              </View>
              <Text className="mt-1 text-xs text-gray-500">
                {item.semester} · {formatPercent(item.percentage)}
              </Text>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
