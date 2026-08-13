import { Stack, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { FlatList, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button, Card, EmptyState, ErrorState, Input, LoadingState } from '@/components/ui';
import { extractMarksErrors, useMarksRoster, useSaveMarks } from '@/features/assessments/api';
import { ApiError } from '@/lib/api/client';

export default function EnterMarksScreen() {
  const { assessmentId } = useLocalSearchParams<{ assessmentId: string }>();
  const id = Number(assessmentId);
  const { data, isPending, isError, error, refetch } = useMarksRoster(id);
  const saveMarks = useSaveMarks(id);
  const [values, setValues] = useState<Record<number, string>>({});
  const [rowErrors, setRowErrors] = useState<string[]>([]);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (data) {
      setValues(
        Object.fromEntries(data.rows.map((row) => [row.student_id, row.obtained_marks?.toString() ?? ''])),
      );
    }
  }, [data]);

  const onSave = async () => {
    setRowErrors([]);
    setSaved(false);
    try {
      await saveMarks.mutateAsync(values);
      setSaved(true);
    } catch (error) {
      const marksErrors = extractMarksErrors(error);
      setRowErrors(
        marksErrors.length > 0
          ? marksErrors
          : [error instanceof ApiError ? error.message : 'Could not save marks.'],
      );
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: data?.assessment.title ?? 'Enter Marks' }} />
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data.rows}
          keyExtractor={(item) => String(item.student_id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListHeaderComponent={
            <Text className="mb-3 text-xs text-gray-500">
              Out of {data.assessment.total_marks} marks. Leave blank to clear a student&apos;s mark.
            </Text>
          }
          ListEmptyComponent={<EmptyState title="No students enrolled in this course" />}
          renderItem={({ item }) => (
            <Card className="flex-row items-center justify-between">
              <View className="flex-1 pr-3">
                <Text className="text-sm font-semibold text-gray-900">{item.name}</Text>
                <Text className="text-xs text-gray-500">{item.roll_number}</Text>
              </View>
              <View className="w-24">
                <Input
                  keyboardType="numeric"
                  placeholder="—"
                  value={values[item.student_id] ?? ''}
                  onChangeText={(text) => setValues((prev) => ({ ...prev, [item.student_id]: text }))}
                />
              </View>
            </Card>
          )}
          ListFooterComponent={
            <View className="mt-2">
              {rowErrors.length > 0 && (
                <View className="mb-3 rounded-xl bg-red-50 px-3.5 py-3">
                  {rowErrors.map((msg, i) => (
                    <Text key={i} className="text-sm text-red-700">
                      {msg}
                    </Text>
                  ))}
                </View>
              )}
              {saved && rowErrors.length === 0 && (
                <Text className="mb-3 text-sm text-green-700">Marks saved.</Text>
              )}
              <Button label="Save Marks" onPress={() => void onSave()} loading={saveMarks.isPending} fullWidth />
            </View>
          }
        />
      )}
    </SafeAreaView>
  );
}
