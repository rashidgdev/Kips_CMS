import { Text, View } from 'react-native';

import { Button } from './Button';

type Props = {
  title: string;
  message?: string;
  actionLabel?: string;
  onAction?: () => void;
};

export function EmptyState({ title, message, actionLabel, onAction }: Props) {
  return (
    <View className="flex-1 items-center justify-center px-8 py-12">
      <Text className="text-center text-base font-semibold text-gray-700">{title}</Text>
      {message && <Text className="mt-1.5 text-center text-sm text-gray-500">{message}</Text>}
      {actionLabel && onAction && (
        <View className="mt-4">
          <Button label={actionLabel} onPress={onAction} variant="secondary" />
        </View>
      )}
    </View>
  );
}
