import { Text, View } from 'react-native';

import { Button, Card } from '@/components/ui';

export function TempPasswordCard({
  username,
  tempPassword,
  onDone,
}: {
  username: string;
  tempPassword: string;
  onDone: () => void;
}) {
  return (
    <Card className="border-green-200 bg-green-50">
      <Text className="text-base font-bold text-green-900">Account created</Text>
      <Text className="mt-2 text-sm text-green-800">
        Share these sign-in details with the new user - they&apos;ll be asked to set their own password on first login.
      </Text>
      <View className="mt-3 rounded-xl bg-white px-3.5 py-3">
        <Text className="text-xs text-gray-500">Username</Text>
        <Text className="text-base font-semibold text-gray-900">{username}</Text>
        <Text className="mt-2 text-xs text-gray-500">Temporary Password</Text>
        <Text className="text-base font-semibold text-gray-900">{tempPassword}</Text>
      </View>
      <View className="mt-3">
        <Button label="Done" onPress={onDone} fullWidth />
      </View>
    </Card>
  );
}
