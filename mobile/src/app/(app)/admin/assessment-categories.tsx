import { Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

import type { FieldConfig } from '@/features/admin/SimpleCrudScreen';
import { SimpleCrudScreen } from '@/features/admin/SimpleCrudScreen';

type AssessmentCategory = { id: number; name: string; default_weight_percent: number };

const fields: FieldConfig[] = [
  { key: 'name', label: 'Name', type: 'text', required: true },
  { key: 'default_weight_percent', label: 'Default Weight %', type: 'number' },
];

export default function AssessmentCategoriesScreen() {
  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Assessment Categories' }} />
      <SimpleCrudScreen<AssessmentCategory>
        basePath="/assessments/categories/"
        fields={fields}
        renderItemLabel={(item) => ({ title: item.name, subtitle: `${item.default_weight_percent}% default weight` })}
      />
    </SafeAreaView>
  );
}
