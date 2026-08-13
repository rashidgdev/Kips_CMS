import { Stack } from 'expo-router';
import { useState } from 'react';
import { FlatList, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Card, ChipPicker, EmptyState, ErrorState, LoadingState } from '@/components/ui';
import { useSimpleCrudList } from '@/features/admin/simpleCrud';
import { useAcademicReport } from '@/features/reports/api';
import { formatPercent } from '@/lib/format';

type Offering = { id: number; course_label: string; section: string };

export default function AcademicReportScreen() {
  const { data: offerings, isPending: offeringsPending } = useSimpleCrudList<Offering>('/academics/offerings/');
  const [offeringId, setOfferingId] = useState<number | null>(null);
  const { data, isPending, isError, error, refetch } = useAcademicReport(offeringId);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Academic Report' }} />
      <View className="px-4 pt-4">
        <Text className="mb-2 text-sm font-medium text-gray-700">Course Offering</Text>
        {offeringsPending ? (
          <LoadingState />
        ) : (
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <ChipPicker
              options={(offerings?.results ?? []).map((o) => ({ value: o.id, label: `${o.course_label} (${o.section})` }))}
              value={offeringId}
              onChange={setOfferingId}
            />
          </ScrollView>
        )}
      </View>

      {offeringId === null ? (
        <EmptyState title="Pick a course offering" />
      ) : isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data.rows}
          keyExtractor={(item) => String(item.student_id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListEmptyComponent={<EmptyState title="No graded students" />}
          renderItem={({ item }) => (
            <Card className="flex-row items-center justify-between">
              <View className="flex-1">
                <Text className="text-sm font-semibold text-gray-900">{item.name}</Text>
                <Text className="text-xs text-gray-500">
                  {item.roll_number} · {item.total_obtained}/{item.total_possible} · {formatPercent(item.percentage)}
                </Text>
              </View>
              {item.grade_letter && <Badge label={item.grade_letter} tone="brand" />}
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
