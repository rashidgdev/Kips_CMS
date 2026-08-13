import Ionicons from '@expo/vector-icons/Ionicons';
import { Stack } from 'expo-router';
import { useState } from 'react';
import { FlatList, Pressable, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button, Card, EmptyState, ErrorState, Input, LoadingState } from '@/components/ui';
import { useEnrollByStudent, useStudentCandidates } from '@/features/enrollment/api';
import { usePeople } from '@/features/people/api';

export default function EnrollByStudentScreen() {
  const [query, setQuery] = useState('');
  const { data: students, isPending: studentsPending } = usePeople({ role: 'student', q: query });
  const [studentId, setStudentId] = useState<number | null>(null);
  const { data, isPending, isError, error, refetch } = useStudentCandidates(studentId);
  const enroll = useEnrollByStudent();
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [message, setMessage] = useState<string | null>(null);

  const toggle = (offeringId: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(offeringId)) next.delete(offeringId);
      else next.add(offeringId);
      return next;
    });
  };

  const onSubmit = () => {
    if (!studentId || selected.size === 0) return;
    setMessage(null);
    enroll.mutate(
      { studentId, offeringIds: Array.from(selected) },
      {
        onSuccess: (result) => {
          setMessage(`Enrolled in ${result.enrolled_count} course(s).`);
          setSelected(new Set());
        },
      },
    );
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Enroll by Student' }} />

      {studentId === null ? (
        <View className="flex-1">
          <View className="px-4 pt-4">
            <Input placeholder="Search student by name or username" value={query} onChangeText={setQuery} />
          </View>
          {studentsPending ? (
            <LoadingState />
          ) : (
            <FlatList
              data={students}
              keyExtractor={(item) => String(item.id)}
              contentContainerClassName="px-4 py-4 gap-2"
              ListEmptyComponent={<EmptyState title="No students found" />}
              renderItem={({ item }) =>
                item.profile_id ? (
                  <Card onPress={() => setStudentId(item.profile_id!)}>
                    <Text className="text-sm font-semibold text-gray-900">{item.full_name}</Text>
                    <Text className="text-xs text-gray-500">{item.identifier}</Text>
                  </Card>
                ) : null
              }
            />
          )}
        </View>
      ) : isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data.offerings}
          keyExtractor={(item) => String(item.id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListHeaderComponent={
            <View className="mb-2 flex-row items-center justify-between">
              <Text className="text-sm text-gray-600">
                {data.student.name} ({data.student.roll_number})
              </Text>
              <Pressable
                accessibilityRole="button"
                onPress={() => {
                  setStudentId(null);
                  setSelected(new Set());
                  setMessage(null);
                }}
              >
                <Text className="text-xs font-medium text-brand-700">Change</Text>
              </Pressable>
            </View>
          }
          ListEmptyComponent={<EmptyState title="No course offerings found for this student's program" />}
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
                  <Text className="text-sm font-semibold text-gray-900">{item.course}</Text>
                  <Text className="text-xs text-gray-500">
                    {item.semester} {item.already_enrolled ? '· Already enrolled' : ''}
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
                label={`Enroll in ${selected.size} Course(s)`}
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
