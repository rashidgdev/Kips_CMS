import { Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

import { LoadingState } from '@/components/ui';
import type { FieldConfig } from '@/features/admin/SimpleCrudScreen';
import { SimpleCrudScreen } from '@/features/admin/SimpleCrudScreen';
import { useSimpleCrudList } from '@/features/admin/simpleCrud';

type FeeStructure = { id: number; program: number; category: number; amount: number; is_recurring: boolean };
type Program = { id: number; code: string };
type FeeCategory = { id: number; name: string };

export default function FeeStructuresScreen() {
  const { data: programs, isPending: programsPending } = useSimpleCrudList<Program>('/academics/programs/');
  const { data: categories, isPending: categoriesPending } = useSimpleCrudList<FeeCategory>('/finance/categories/');
  if (programsPending || categoriesPending) return <LoadingState />;

  const fields: FieldConfig[] = [
    {
      key: 'program', label: 'Program', type: 'picker', required: true,
      options: (programs?.results ?? []).map((p) => ({ value: p.id, label: p.code })),
    },
    {
      key: 'category', label: 'Fee Category', type: 'picker', required: true,
      options: (categories?.results ?? []).map((c) => ({ value: c.id, label: c.name })),
    },
    { key: 'amount', label: 'Amount', type: 'number', required: true },
    { key: 'is_recurring', label: 'Recurring (every semester)', type: 'boolean' },
  ];

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Fee Structures' }} />
      <SimpleCrudScreen<FeeStructure>
        basePath="/finance/structures/"
        fields={fields}
        renderItemLabel={(item) => ({ title: `Rs. ${item.amount}`, subtitle: item.is_recurring ? 'Recurring' : 'One-time' })}
      />
    </SafeAreaView>
  );
}
