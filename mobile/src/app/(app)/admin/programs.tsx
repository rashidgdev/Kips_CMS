import { Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

import { LoadingState } from '@/components/ui';
import type { FieldConfig } from '@/features/admin/SimpleCrudScreen';
import { SimpleCrudScreen } from '@/features/admin/SimpleCrudScreen';
import { useSimpleCrudList } from '@/features/admin/simpleCrud';

type Program = { id: number; name: string; code: string; department: number; total_semesters: number; degree_level: string };
type Department = { id: number; name: string; code: string };

const DEGREE_LEVELS = [
  { value: 'bachelors', label: "Bachelor's" },
  { value: 'associate', label: 'Associate' },
  { value: 'diploma', label: 'Diploma' },
];

export default function ProgramsScreen() {
  const { data: departments, isPending } = useSimpleCrudList<Department>('/accounts/departments/');
  if (isPending) return <LoadingState />;

  const fields: FieldConfig[] = [
    { key: 'name', label: 'Name', type: 'text', required: true },
    { key: 'code', label: 'Code', type: 'text', required: true },
    {
      key: 'department',
      label: 'Department',
      type: 'picker',
      required: true,
      options: (departments?.results ?? []).map((d) => ({ value: d.id, label: d.code })),
    },
    { key: 'total_semesters', label: 'Total Semesters', type: 'number' },
    { key: 'degree_level', label: 'Degree Level', type: 'picker', options: DEGREE_LEVELS },
  ];

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Programs' }} />
      <SimpleCrudScreen<Program>
        basePath="/academics/programs/"
        fields={fields}
        renderItemLabel={(item) => ({ title: `${item.code} - ${item.name}`, subtitle: `${item.total_semesters} semesters` })}
      />
    </SafeAreaView>
  );
}
