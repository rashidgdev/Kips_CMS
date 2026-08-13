import { Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

import { LoadingState } from '@/components/ui';
import type { FieldConfig } from '@/features/admin/SimpleCrudScreen';
import { SimpleCrudScreen } from '@/features/admin/SimpleCrudScreen';
import { useSimpleCrudList } from '@/features/admin/simpleCrud';

type Course = { id: number; program: number; code: string; title: string; credit_hours: number; semester_number: number; course_type: string };
type Program = { id: number; name: string; code: string };

const COURSE_TYPES = [
  { value: 'theory', label: 'Theory' },
  { value: 'lab', label: 'Lab' },
];

export default function CoursesScreen() {
  const { data: programs, isPending } = useSimpleCrudList<Program>('/academics/programs/');
  if (isPending) return <LoadingState />;

  const fields: FieldConfig[] = [
    {
      key: 'program', label: 'Program', type: 'picker', required: true,
      options: (programs?.results ?? []).map((p) => ({ value: p.id, label: p.code })),
    },
    { key: 'code', label: 'Course Code', type: 'text', required: true },
    { key: 'title', label: 'Title', type: 'text', required: true },
    { key: 'credit_hours', label: 'Credit Hours', type: 'number' },
    { key: 'semester_number', label: 'Semester Number', type: 'number', required: true },
    { key: 'course_type', label: 'Type', type: 'picker', options: COURSE_TYPES },
  ];

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Courses' }} />
      <SimpleCrudScreen<Course>
        basePath="/academics/courses/"
        fields={fields}
        renderItemLabel={(item) => ({ title: `${item.code} - ${item.title}`, subtitle: `${item.credit_hours} credit hours` })}
      />
    </SafeAreaView>
  );
}
