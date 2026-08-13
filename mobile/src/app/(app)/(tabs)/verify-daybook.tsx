import Ionicons from '@expo/vector-icons/Ionicons';
import { router } from 'expo-router';
import { FlatList, Pressable, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button, Card, EmptyState, ErrorState, LoadingState } from '@/components/ui';
import { useVerifyEntry, useVerifyQueue } from '@/features/daybook/api';

export default function VerifyDayBookScreen() {
  const { data, isPending, isError, error, refetch } = useVerifyQueue();
  const verifyEntry = useVerifyEntry();

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data}
          keyExtractor={(item) => String(item.id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListHeaderComponent={
            <Pressable
              accessibilityRole="button"
              onPress={() => router.push('/daybook/workload')}
              className="mb-4 flex-row items-center justify-center gap-1.5 rounded-xl border border-gray-300 bg-white py-3"
            >
              <Ionicons name="bar-chart" size={16} color="#1d4ed8" />
              <Text className="text-sm font-semibold text-brand-700">View Workload Report</Text>
            </Pressable>
          }
          ListEmptyComponent={<EmptyState title="Nothing to verify" message="All day book entries are up to date." />}
          renderItem={({ item }) => (
            <Card>
              <Text className="text-sm font-semibold text-gray-900">{item.course}</Text>
              <Text className="mt-0.5 text-xs text-gray-500">
                {item.teacher} · {item.session_date}
                {item.topic_covered ? ` · ${item.topic_covered}` : ''}
              </Text>
              <View className="mt-2">
                <Button
                  label="Verify"
                  variant="secondary"
                  loading={verifyEntry.isPending}
                  onPress={() => verifyEntry.mutate({ entryId: item.id, remarks: '' })}
                />
              </View>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
