import { Stack } from 'expo-router';
import { useState } from 'react';
import { FlatList, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Card, ChipPicker, EmptyState, ErrorState, LoadingState } from '@/components/ui';
import { useSimpleCrudList } from '@/features/admin/simpleCrud';
import { useMeritList } from '@/features/reports/api';

type Semester = { id: number; name: string; academic_year: string };

export default function MeritListScreen() {
  const { data: semesters, isPending: semestersPending } = useSimpleCrudList<Semester>('/academics/semesters/');
  const [semesterId, setSemesterId] = useState<number | null>(null);
  const { data, isPending, isError, error, refetch } = useMeritList(semesterId);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Merit List' }} />
      <View className="px-4 pt-4">
        <Text className="mb-2 text-sm font-medium text-gray-700">Semester</Text>
        {semestersPending ? (
          <LoadingState />
        ) : (
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <ChipPicker
              options={(semesters?.results ?? []).map((s) => ({ value: s.id, label: `${s.name} (${s.academic_year})` }))}
              value={semesterId}
              onChange={setSemesterId}
            />
          </ScrollView>
        )}
      </View>

      {semesterId === null ? (
        <EmptyState title="Pick a semester" />
      ) : isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data.rows}
          keyExtractor={(item) => String(item.student_id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListEmptyComponent={<EmptyState title="No GPA data for this semester" />}
          renderItem={({ item }) => (
            <Card className="flex-row items-center gap-3">
              <Text className="w-8 text-center text-base font-bold text-brand-700">#{item.rank}</Text>
              <View className="flex-1">
                <Text className="text-sm font-semibold text-gray-900">{item.name}</Text>
                <Text className="text-xs text-gray-500">{item.roll_number}</Text>
              </View>
              <Text className="text-base font-bold text-gray-900">{item.gpa.toFixed(2)}</Text>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
