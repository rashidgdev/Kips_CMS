import { Text, View } from 'react-native';

import { ApiError } from '@/lib/api/client';

import { Button } from './Button';

type Props = {
  error: unknown;
  onRetry?: () => void;
};

function messageFor(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 403) return "You don't have permission to view this.";
    if (error.status === 404) return 'Not found.';
    return error.message;
  }
  if (error instanceof Error) return error.message;
  return 'Something went wrong.';
}

export function ErrorState({ error, onRetry }: Props) {
  return (
    <View className="flex-1 items-center justify-center px-8 py-12">
      <Text className="text-center text-base font-semibold text-gray-800">{messageFor(error)}</Text>
      {onRetry && (
        <View className="mt-4">
          <Button label="Try again" onPress={onRetry} variant="secondary" />
        </View>
      )}
    </View>
  );
}
