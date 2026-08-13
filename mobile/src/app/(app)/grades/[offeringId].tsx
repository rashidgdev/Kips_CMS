import { Stack, useLocalSearchParams } from 'expo-router';
import { FlatList, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Card, EmptyState, ErrorState, LoadingState, StatCard } from '@/components/ui';
import { useStudentCourseGrades } from '@/features/assessments/api';
import { formatPercent } from '@/lib/format';

export default function StudentCourseGradesScreen() {
  const { offeringId } = useLocalSearchParams<{ offeringId: string }>();
  const id = Number(offeringId);
  const { data, isPending, isError, error, refetch } = useStudentCourseGrades(id);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: data?.course ?? 'Grades' }} />
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data.marks}
          keyExtractor={(item) => String(item.assessment_id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListHeaderComponent={
            <View className="mb-4 flex-row gap-3">
              <StatCard
                label="Score"
                value={data.total_obtained !== null ? `${data.total_obtained}/${data.total_possible}` : '—'}
              />
              <StatCard label="Percentage" value={formatPercent(data.percentage)} />
              <StatCard label="Grade" value={data.grade_letter ?? '—'} />
            </View>
          }
          ListEmptyComponent={<EmptyState title="No marks entered yet" />}
          renderItem={({ item }) => (
            <Card className="flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-sm font-semibold text-gray-900">{item.title}</Text>
                <Text className="mt-0.5 text-xs text-gray-500">{item.category}</Text>
              </View>
              <Badge label={`${item.obtained_marks}/${item.total_marks}`} tone="brand" />
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
