import { ActivityIndicator, Text, View } from 'react-native';

import { Colors } from '@/constants/theme';

export function LoadingState({ label = 'Loading…' }: { label?: string }) {
  return (
    <View className="flex-1 items-center justify-center py-12">
      <ActivityIndicator size="large" color={Colors.brand} />
      <Text className="mt-3 text-sm text-gray-500">{label}</Text>
    </View>
  );
}
