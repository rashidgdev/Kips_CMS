import { Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

import { LoadingState } from '@/components/ui';
import type { FieldConfig } from '@/features/admin/SimpleCrudScreen';
import { SimpleCrudScreen } from '@/features/admin/SimpleCrudScreen';
import { useSimpleCrudList } from '@/features/admin/simpleCrud';
import { usePeople } from '@/features/people/api';

type CourseOffering = {
  id: number; course: number; semester: number; teacher: number; section: string; max_seats: number; is_active: boolean;
};
type Course = { id: number; code: string; title: string };
type Semester = { id: number; name: string; academic_year: string };

export default function OfferingsScreen() {
  const { data: courses, isPending: coursesPending } = useSimpleCrudList<Course>('/academics/courses/');
  const { data: semesters, isPending: semestersPending } = useSimpleCrudList<Semester>('/academics/semesters/');
  const { data: teachers, isPending: teachersPending } = usePeople({ role: 'teacher' });
  const { data: hods, isPending: hodsPending } = usePeople({ role: 'hod' });

  if (coursesPending || semestersPending || teachersPending || hodsPending) return <LoadingState />;

  const teacherOptions = [...(teachers ?? []), ...(hods ?? [])]
    .filter((t) => t.profile_id !== null)
    .map((t) => ({ value: t.profile_id as number, label: t.full_name }));

  const fields: FieldConfig[] = [
    {
      key: 'course', label: 'Course', type: 'picker', required: true,
      options: (courses?.results ?? []).map((c) => ({ value: c.id, label: c.code })),
    },
    {
      key: 'semester', label: 'Semester', type: 'picker', required: true,
      options: (semesters?.results ?? []).map((s) => ({ value: s.id, label: `${s.name} (${s.academic_year})` })),
    },
    { key: 'teacher', label: 'Teacher', type: 'picker', required: true, options: teacherOptions },
    { key: 'section', label: 'Section', type: 'text' },
    { key: 'max_seats', label: 'Max Seats', type: 'number' },
    { key: 'is_active', label: 'Active', type: 'boolean' },
  ];

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Course Offerings' }} />
      <SimpleCrudScreen<CourseOffering>
        basePath="/academics/offerings/"
        fields={fields}
        renderItemLabel={(item) => ({ title: `Offering #${item.id} · Section ${item.section}`, subtitle: item.is_active ? 'Active' : 'Inactive' })}
      />
    </SafeAreaView>
  );
}
