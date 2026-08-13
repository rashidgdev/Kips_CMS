import { router } from 'expo-router';
import { FlatList, RefreshControl, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Card, EmptyState, ErrorState, LoadingState } from '@/components/ui';
import { useStudentFeeSummary } from '@/features/finance/api';
import { formatCurrency } from '@/lib/format';

export default function StudentFeesScreen() {
  const { data, isPending, isError, error, refetch, isRefetching } = useStudentFeeSummary();

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data}
          keyExtractor={(item) => String(item.student_id)}
          contentContainerClassName="px-4 py-4 gap-2"
          refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={() => void refetch()} />}
          ListEmptyComponent={<EmptyState title="No students found" />}
          renderItem={({ item }) => (
            <Card
              onPress={() =>
                router.push({ pathname: '/finance/student/[studentId]', params: { studentId: String(item.student_id) } })
              }
            >
              <View className="flex-row items-center justify-between">
                <Text className="text-sm font-semibold text-gray-900">{item.name}</Text>
                <Text className="text-xs text-gray-500">{item.roll_number}</Text>
              </View>
              <Text className="mt-0.5 text-xs text-gray-500">{item.program}</Text>
              <Text className="mt-1 text-xs text-gray-600">
                Outstanding: {formatCurrency(item.total_outstanding)}
              </Text>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
