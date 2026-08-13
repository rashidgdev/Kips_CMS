import { router, Stack } from 'expo-router';
import { useState } from 'react';
import { FlatList, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Card, EmptyState, ErrorState, Input, LoadingState } from '@/components/ui';
import { useProgressStudentSearch } from '@/features/reports/api';

export default function ProgressSearchScreen() {
  const [query, setQuery] = useState('');
  const { data, isPending, isError, error, refetch } = useProgressStudentSearch(query);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Student Progress Report' }} />
      <View className="px-4 pt-4">
        <Input placeholder="Search by name, roll number, or username" value={query} onChangeText={setQuery} />
      </View>
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data}
          keyExtractor={(item) => String(item.id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListEmptyComponent={<EmptyState title="No students found" />}
          renderItem={({ item }) => (
            <Card
              onPress={() =>
                router.push({ pathname: '/reports/progress/[studentId]', params: { studentId: String(item.id) } })
              }
            >
              <Text className="text-sm font-semibold text-gray-900">{item.name}</Text>
              <Text className="text-xs text-gray-500">{item.roll_number}</Text>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
