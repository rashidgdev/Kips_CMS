import { Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Card } from '@/components/ui';

/** Stands in for a module screen not built yet - each later phase replaces the call site, not this component. */
export function PlaceholderScreen({ title, phase }: { title: string; phase: string }) {
  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      <View className="flex-1 items-center justify-center px-6">
        <Card className="w-full items-center">
          <Text className="text-lg font-semibold text-gray-900">{title}</Text>
          <Text className="mt-2 text-center text-sm text-gray-500">
            This screen is built in {phase} of the mobile rollout.
          </Text>
        </Card>
      </View>
    </SafeAreaView>
  );
}
