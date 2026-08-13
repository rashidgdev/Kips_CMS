import { router } from 'expo-router';
import { FlatList, RefreshControl, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Card, EmptyState, ErrorState, LoadingState } from '@/components/ui';
import { useStudentAttendanceOverview, useTeacherOfferings } from '@/features/attendance/api';
import { formatPercent } from '@/lib/format';
import { useAuth } from '@/lib/auth/AuthContext';

function TeacherOfferingsList() {
  const { data, isPending, isError, error, refetch, isRefetching } = useTeacherOfferings();

  if (isPending) return <LoadingState />;
  if (isError) return <ErrorState error={error} onRetry={() => void refetch()} />;

  return (
    <FlatList
      data={data}
      keyExtractor={(item) => String(item.id)}
      contentContainerClassName="px-4 py-4 gap-2"
      refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={() => void refetch()} />}
      ListEmptyComponent={<EmptyState title="No course offerings assigned" />}
      renderItem={({ item }) => (
        <Card
          onPress={() =>
            router.push({ pathname: '/attendance/offering/[offeringId]', params: { offeringId: String(item.id) } })
          }
        >
          <Text className="text-sm font-semibold text-gray-900">{item.course}</Text>
          <Text className="mt-0.5 text-xs text-gray-500">
            {item.semester} · Section {item.section}
          </Text>
        </Card>
      )}
    />
  );
}

function StudentAttendanceList() {
  const { data, isPending, isError, error, refetch, isRefetching } = useStudentAttendanceOverview();

  if (isPending) return <LoadingState />;
  if (isError) return <ErrorState error={error} onRetry={() => void refetch()} />;

  return (
    <FlatList
      data={data}
      keyExtractor={(item) => String(item.course_offering_id)}
      contentContainerClassName="px-4 py-4 gap-2"
      refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={() => void refetch()} />}
      ListEmptyComponent={<EmptyState title="No enrolled courses" />}
      renderItem={({ item }) => (
        <Card
          onPress={() =>
            router.push({
              pathname: '/attendance/my/[offeringId]',
              params: { offeringId: String(item.course_offering_id) },
            })
          }
        >
          <View className="flex-row items-center justify-between">
            <Text className="flex-1 text-sm font-semibold text-gray-900">{item.course}</Text>
            <Badge
              label={formatPercent(item.percentage)}
              tone={item.is_shortage ? 'danger' : 'success'}
            />
          </View>
          <Text className="mt-1 text-xs text-gray-500">
            {item.attended}/{item.delivered} attended · {item.absent} absent
          </Text>
          {item.is_shortage && (
            <Text className="mt-1 text-xs font-medium text-red-600">
              Below the {item.threshold}% attendance requirement
            </Text>
          )}
        </Card>
      )}
    />
  );
}

export default function AttendanceScreen() {
  const { user } = useAuth();
  const isTeacher = user?.role === 'teacher' || user?.role === 'hod';

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      {isTeacher ? <TeacherOfferingsList /> : <StudentAttendanceList />}
    </SafeAreaView>
  );
}
