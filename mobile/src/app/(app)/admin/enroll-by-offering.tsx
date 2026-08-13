import Ionicons from '@expo/vector-icons/Ionicons';
import { Stack } from 'expo-router';
import { useState } from 'react';
import { FlatList, Pressable, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button, Card, ChipPicker, EmptyState, ErrorState, LoadingState } from '@/components/ui';
import { useSimpleCrudList } from '@/features/admin/simpleCrud';
import { useEnrollByOffering, useOfferingCandidates } from '@/features/enrollment/api';

type CourseOfferingOption = { id: number; course_label: string; semester_label: string; section: string };

export default function EnrollByOfferingScreen() {
  const { data: offerings, isPending: offeringsPending } = useSimpleCrudList<CourseOfferingOption>('/academics/offerings/');
  const [offeringId, setOfferingId] = useState<number | null>(null);
  const { data, isPending, isError, error, refetch } = useOfferingCandidates(offeringId);
  const enroll = useEnrollByOffering();
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [message, setMessage] = useState<string | null>(null);

  const toggle = (studentId: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(studentId)) next.delete(studentId);
      else next.add(studentId);
      return next;
    });
  };

  const onSubmit = () => {
    if (!offeringId || selected.size === 0) return;
    setMessage(null);
    enroll.mutate(
      { offeringId, studentIds: Array.from(selected) },
      {
        onSuccess: (result) => {
          setMessage(`Enrolled ${result.enrolled_count} student(s).`);
          setSelected(new Set());
        },
      },
    );
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Enroll by Offering' }} />
      <View className="px-4 pt-4">
        <Text className="mb-2 text-sm font-medium text-gray-700">Course Offering</Text>
        {offeringsPending ? (
          <LoadingState />
        ) : (
          <ChipPicker
            options={(offerings?.results ?? []).map((o) => ({ value: o.id, label: `${o.course_label} (${o.section})` }))}
            value={offeringId}
            onChange={(v) => {
              setOfferingId(v);
              setSelected(new Set());
              setMessage(null);
            }}
          />
        )}
      </View>

      {offeringId === null ? (
        <EmptyState title="Pick a course offering" message="Its program-matched active students will appear here." />
      ) : isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data.students}
          keyExtractor={(item) => String(item.id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListEmptyComponent={<EmptyState title="No active students found for this program" />}
          renderItem={({ item }) => (
            <Pressable
              accessibilityRole="checkbox"
              accessibilityState={{ checked: item.already_enrolled || selected.has(item.id) }}
              disabled={item.already_enrolled}
              onPress={() => toggle(item.id)}
            >
              <Card className={`flex-row items-center gap-3 ${item.already_enrolled ? 'opacity-50' : ''}`}>
                <Ionicons
                  name={item.already_enrolled || selected.has(item.id) ? 'checkbox' : 'square-outline'}
                  size={20}
                  color={item.already_enrolled ? '#9ca3af' : '#1d4ed8'}
                />
                <View className="flex-1">
                  <Text className="text-sm font-semibold text-gray-900">{item.name}</Text>
                  <Text className="text-xs text-gray-500">
                    {item.roll_number} {item.already_enrolled ? '· Already enrolled' : ''}
                  </Text>
                </View>
              </Card>
            </Pressable>
          )}
          ListFooterComponent={
            <View className="mt-2">
              {message && <Text className="mb-3 text-sm text-green-700">{message}</Text>}
              {enroll.isError && <Text className="mb-3 text-sm text-red-600">{enroll.error.message}</Text>}
              <Button
                label={`Enroll ${selected.size} Student(s)`}
                onPress={onSubmit}
                loading={enroll.isPending}
                fullWidth
              />
            </View>
          }
        />
      )}
    </SafeAreaView>
  );
}
