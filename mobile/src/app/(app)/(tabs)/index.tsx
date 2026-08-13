import { RefreshControl, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ErrorState, LoadingState } from '@/components/ui';
import { AccountantDashboard } from '@/features/dashboard/AccountantDashboard';
import { AdminDashboard } from '@/features/dashboard/AdminDashboard';
import { useDashboard } from '@/features/dashboard/api';
import { CoordinatorDashboard } from '@/features/dashboard/CoordinatorDashboard';
import { StudentDashboard } from '@/features/dashboard/StudentDashboard';
import { TeacherDashboard } from '@/features/dashboard/TeacherDashboard';
import type { DashboardData } from '@/features/dashboard/types';
import { useAuth } from '@/lib/auth/AuthContext';

function DashboardContent({ data }: { data: DashboardData }) {
  switch (data.role) {
    case 'student':
      return <StudentDashboard data={data} />;
    case 'teacher':
    case 'hod':
      return <TeacherDashboard data={data} />;
    case 'coordinator':
      return <CoordinatorDashboard data={data} />;
    case 'accountant':
      return <AccountantDashboard data={data} />;
    case 'admin':
      return <AdminDashboard data={data} />;
  }
}

export default function DashboardScreen() {
  const { user } = useAuth();
  const { data, isPending, isError, error, refetch, isRefetching } = useDashboard();

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      <ScrollView
        contentContainerClassName="px-4 py-4"
        refreshControl={<RefreshControl refreshing={isRefetching} onRefresh={() => void refetch()} />}
      >
        <View className="mb-4">
          <Text className="text-sm text-gray-500">Welcome back,</Text>
          <Text className="text-xl font-bold text-gray-900">{user?.full_name}</Text>
        </View>

        {isPending ? (
          <LoadingState />
        ) : isError ? (
          <ErrorState error={error} onRetry={() => void refetch()} />
        ) : (
          <DashboardContent data={data} />
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
