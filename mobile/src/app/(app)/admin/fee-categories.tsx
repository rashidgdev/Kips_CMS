import { Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

import type { FieldConfig } from '@/features/admin/SimpleCrudScreen';
import { SimpleCrudScreen } from '@/features/admin/SimpleCrudScreen';

type FeeCategory = { id: number; name: string };

const fields: FieldConfig[] = [{ key: 'name', label: 'Name', type: 'text', required: true }];

export default function FeeCategoriesScreen() {
  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Fee Categories' }} />
      <SimpleCrudScreen<FeeCategory> basePath="/finance/categories/" fields={fields} renderItemLabel={(item) => ({ title: item.name })} />
    </SafeAreaView>
  );
}
