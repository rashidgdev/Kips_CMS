import { Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

import { LoadingState } from '@/components/ui';
import type { FieldConfig } from '@/features/admin/SimpleCrudScreen';
import { SimpleCrudScreen } from '@/features/admin/SimpleCrudScreen';
import { useSimpleCrudList } from '@/features/admin/simpleCrud';

type Semester = {
  id: number; program: number; number: number; name: string; academic_year: string;
  start_date: string; end_date: string; is_current: boolean;
};
type Program = { id: number; name: string; code: string };

export default function SemestersScreen() {
  const { data: programs, isPending } = useSimpleCrudList<Program>('/academics/programs/');
  if (isPending) return <LoadingState />;

  const fields: FieldConfig[] = [
    {
      key: 'program', label: 'Program', type: 'picker', required: true,
      options: (programs?.results ?? []).map((p) => ({ value: p.id, label: p.code })),
    },
    { key: 'number', label: 'Semester Number', type: 'number', required: true },
    { key: 'name', label: 'Name', type: 'text' },
    { key: 'academic_year', label: 'Academic Year', type: 'text', required: true },
    { key: 'start_date', label: 'Start Date', type: 'date', required: true },
    { key: 'end_date', label: 'End Date', type: 'date', required: true },
    { key: 'is_current', label: 'Currently Running', type: 'boolean' },
  ];

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Semesters' }} />
      <SimpleCrudScreen<Semester>
        basePath="/academics/semesters/"
        fields={fields}
        renderItemLabel={(item) => ({
          title: `${item.name || `Semester ${item.number}`} (${item.academic_year})`,
          subtitle: item.is_current ? 'Currently running' : undefined,
        })}
      />
    </SafeAreaView>
  );
}
