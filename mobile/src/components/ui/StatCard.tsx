import { Text, View } from 'react-native';

export function StatCard({
  label,
  value,
  tone = 'default',
}: {
  label: string;
  value: string | number;
  tone?: 'default' | 'danger' | 'success';
}) {
  const valueClass =
    tone === 'danger' ? 'text-red-600' : tone === 'success' ? 'text-green-600' : 'text-gray-900';
  return (
    <View className="flex-1 rounded-2xl border border-gray-200 bg-white p-4">
      <Text className="text-xs font-medium text-gray-500">{label}</Text>
      <Text className={`mt-1 text-2xl font-bold ${valueClass}`}>{value}</Text>
    </View>
  );
}
