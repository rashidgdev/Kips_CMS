import { router } from 'expo-router';
import { FlatList, RefreshControl, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Card, EmptyState, ErrorState, LoadingState } from '@/components/ui';
import { useTeacherOfferings } from '@/features/assessments/api';

export default function AssessmentsScreen() {
  const { data, isPending, isError, error, refetch, isRefetching } = useTeacherOfferings();

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
          refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={() => void refetch()} />}
          ListEmptyComponent={<EmptyState title="No course offerings assigned" />}
          renderItem={({ item }) => (
            <Card
              onPress={() =>
                router.push({ pathname: '/assessments/offering/[offeringId]', params: { offeringId: String(item.id) } })
              }
            >
              <Text className="text-sm font-semibold text-gray-900">{item.course}</Text>
              <Text className="mt-0.5 text-xs text-gray-500">
                {item.semester} · Section {item.section}
              </Text>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
