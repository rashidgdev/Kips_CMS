import Ionicons from '@expo/vector-icons/Ionicons';
import { router } from 'expo-router';
import { Pressable, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { useAuth } from '@/lib/auth/AuthContext';

export default function ReportsScreen() {
  const { user } = useAuth();

  if (user?.role === 'student' && user.profile) {
    router.replace({ pathname: '/reports/progress/[studentId]', params: { studentId: String(user.profile.id) } });
    return null;
  }

  const items = [
    { label: 'Attendance Report', route: '/reports/attendance' as const, icon: 'checkmark-done' as const },
    { label: 'Academic Report', route: '/reports/academic' as const, icon: 'document-text' as const },
    ...(user?.role === 'coordinator' || user?.role === 'admin'
      ? [{ label: 'Merit List', route: '/reports/merit-list' as const, icon: 'trophy' as const }]
      : []),
    { label: 'Student Progress Report', route: '/reports/progress-search' as const, icon: 'search' as const },
  ];

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      <View className="px-4 py-4">
        <View className="overflow-hidden rounded-2xl border border-gray-200 bg-white">
          {items.map((item, index) => (
            <Pressable
              key={item.route}
              accessibilityRole="button"
              onPress={() => router.push(item.route)}
              className={`flex-row items-center px-4 py-3.5 active:bg-gray-50 ${index > 0 ? 'border-t border-gray-100' : ''}`}
            >
              <Ionicons name={item.icon} size={20} color="#4b5563" />
              <Text className="ml-3 flex-1 text-base text-gray-800">{item.label}</Text>
              <Ionicons name="chevron-forward" size={18} color="#9ca3af" />
            </Pressable>
          ))}
        </View>
      </View>
    </SafeAreaView>
  );
}
