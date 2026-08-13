import { Stack, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { FlatList, Pressable, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button, Card, EmptyState, ErrorState, LoadingState } from '@/components/ui';
import { useMarkAttendance, useRoster } from '@/features/attendance/api';
import type { AttendanceStatus } from '@/features/attendance/types';
import { ApiError } from '@/lib/api/client';

const STATUS_LABELS: Record<AttendanceStatus, string> = {
  present: 'Present',
  absent: 'Absent',
  leave: 'Leave',
  late: 'Late',
};

const STATUS_CLASSES: Record<AttendanceStatus, string> = {
  present: 'bg-green-600 border-green-600',
  absent: 'bg-red-600 border-red-600',
  leave: 'bg-amber-500 border-amber-500',
  late: 'bg-blue-500 border-blue-500',
};

function StatusPicker({
  value,
  onChange,
}: {
  value: AttendanceStatus;
  onChange: (status: AttendanceStatus) => void;
}) {
  const options: AttendanceStatus[] = ['present', 'absent', 'leave', 'late'];
  return (
    <View className="mt-2 flex-row gap-1.5">
      {options.map((status) => {
        const selected = value === status;
        return (
          <Pressable
            key={status}
            accessibilityRole="button"
            accessibilityState={{ selected }}
            onPress={() => onChange(status)}
            className={`rounded-lg border px-2.5 py-1.5 ${
              selected ? STATUS_CLASSES[status] : 'border-gray-300 bg-white'
            }`}
          >
            <Text className={`text-xs font-medium ${selected ? 'text-white' : 'text-gray-600'}`}>
              {STATUS_LABELS[status].slice(0, 4)}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}

export default function MarkAttendanceScreen() {
  const { sessionId } = useLocalSearchParams<{ sessionId: string }>();
  const id = Number(sessionId);
  const { data, isPending, isError, error, refetch } = useRoster(id);
  const markAttendance = useMarkAttendance(id);
  const [statuses, setStatuses] = useState<Record<number, AttendanceStatus>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (data) {
      setStatuses(Object.fromEntries(data.rows.map((row) => [row.student_id, row.status])));
    }
  }, [data]);

  const onSave = async () => {
    setFormError(null);
    setSaved(false);
    try {
      await markAttendance.mutateAsync(statuses);
      setSaved(true);
    } catch (error) {
      setFormError(error instanceof ApiError ? error.message : 'Could not save attendance.');
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: data ? data.session.date : 'Mark Attendance' }} />
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data.rows}
          keyExtractor={(item) => String(item.student_id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListEmptyComponent={<EmptyState title="No students enrolled in this course" />}
          renderItem={({ item }) => (
            <Card>
              <Text className="text-sm font-semibold text-gray-900">{item.name}</Text>
              <Text className="text-xs text-gray-500">{item.roll_number}</Text>
              <StatusPicker
                value={statuses[item.student_id] ?? 'present'}
                onChange={(status) => setStatuses((prev) => ({ ...prev, [item.student_id]: status }))}
              />
            </Card>
          )}
          ListFooterComponent={
            <View className="mt-2">
              {formError && <Text className="mb-3 text-sm text-red-600">{formError}</Text>}
              {saved && !formError && (
                <Text className="mb-3 text-sm text-green-700">Attendance saved.</Text>
              )}
              <Button label="Save Attendance" onPress={() => void onSave()} loading={markAttendance.isPending} fullWidth />
            </View>
          }
        />
      )}
    </SafeAreaView>
  );
}
