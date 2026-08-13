import Ionicons from '@expo/vector-icons/Ionicons';
import { router } from 'expo-router';
import { Pressable, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Button, Card } from '@/components/ui';
import { NAV_CONFIG } from '@/constants/navConfig';
import { useAuth } from '@/lib/auth/AuthContext';

export default function MoreScreen() {
  const { user, logout } = useAuth();
  if (!user) return null;
  const secondaryLinks = NAV_CONFIG[user.role].more;

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      <View className="flex-1 px-4 py-4">
        <Card className="mb-4">
          <Text className="text-lg font-bold text-gray-900">{user.full_name}</Text>
          <Text className="mt-0.5 text-sm text-gray-500">@{user.username}</Text>
          <View className="mt-2 flex-row items-center gap-2">
            <Badge label={user.role_display} tone="brand" />
          </View>
        </Card>

        {secondaryLinks.length > 0 && (
          <Card className="mb-4 p-0">
            {secondaryLinks.map((item, index) => (
              <Pressable
                key={item.key}
                accessibilityRole="button"
                onPress={() => router.push(item.route as never)}
                className={`flex-row items-center px-4 py-3.5 active:bg-gray-50 ${
                  index > 0 ? 'border-t border-gray-100' : ''
                }`}
              >
                <Ionicons name={item.icon} size={20} color="#4b5563" />
                <Text className="ml-3 flex-1 text-base text-gray-800">{item.label}</Text>
                <Ionicons name="chevron-forward" size={18} color="#9ca3af" />
              </Pressable>
            ))}
          </Card>
        )}

        <Pressable
          accessibilityRole="button"
          onPress={() => router.push('/profile' as never)}
          className="mb-4 flex-row items-center rounded-2xl border border-gray-200 bg-white px-4 py-3.5 active:bg-gray-50"
        >
          <Ionicons name="person-circle-outline" size={20} color="#4b5563" />
          <Text className="ml-3 flex-1 text-base text-gray-800">My Profile</Text>
          <Ionicons name="chevron-forward" size={18} color="#9ca3af" />
        </Pressable>

        <View className="mt-auto">
          <Button label="Log out" variant="danger" onPress={() => void logout()} />
        </View>
      </View>
    </SafeAreaView>
  );
}
