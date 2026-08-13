import { Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

import { LoadingState } from '@/components/ui';
import type { FieldConfig } from '@/features/admin/SimpleCrudScreen';
import { SimpleCrudScreen } from '@/features/admin/SimpleCrudScreen';
import { usePeople } from '@/features/people/api';

type Department = { id: number; name: string; code: string; hod: number | null; hod_label: string | null };

export default function DepartmentsScreen() {
  const { data: hods, isPending } = usePeople({ role: 'hod' });

  if (isPending) return <LoadingState />;

  const fields: FieldConfig[] = [
    { key: 'name', label: 'Name', type: 'text', required: true },
    { key: 'code', label: 'Code', type: 'text', required: true },
    {
      key: 'hod',
      label: 'Head of Department',
      type: 'picker',
      options: (hods ?? []).map((h) => ({ value: h.id, label: h.full_name })),
    },
  ];

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Departments' }} />
      <SimpleCrudScreen<Department>
        basePath="/accounts/departments/"
        fields={fields}
        renderItemLabel={(item) => ({ title: `${item.code} - ${item.name}`, subtitle: item.hod_label ?? undefined })}
      />
    </SafeAreaView>
  );
}
