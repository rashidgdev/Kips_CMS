import { Text, View } from 'react-native';

import { Badge, Card, EmptyState, StatCard } from '@/components/ui';
import { formatPercent } from '@/lib/format';

import type { StudentDashboard as StudentDashboardData } from './types';

const STATUS_TONE = { enrolled: 'success', dropped: 'danger', completed: 'brand' } as const;

export function StudentDashboard({ data }: { data: StudentDashboardData }) {
  return (
    <View className="gap-4">
      <View className="flex-row gap-3">
        <StatCard label="CGPA" value={data.cgpa?.toFixed(2) ?? '—'} />
        <StatCard label="Semester GPA" value={data.current_semester_gpa?.toFixed(2) ?? '—'} />
        <StatCard label="Attendance" value={formatPercent(data.overall_attendance_percent)} />
      </View>

      <View>
        <Text className="mb-2 text-base font-semibold text-gray-900">My Courses</Text>
        {data.enrollments.length === 0 ? (
          <EmptyState title="No enrollments yet" message="Your enrolled courses will show up here." />
        ) : (
          <View className="gap-2">
            {data.enrollments.map((e) => (
              <Card key={e.id} className="flex-row items-center justify-between">
                <View className="flex-1">
                  <Text className="text-sm font-semibold text-gray-900">{e.course}</Text>
                  <Text className="mt-0.5 text-xs text-gray-500">{e.teacher}</Text>
                </View>
                <Badge
                  label={e.status}
                  tone={STATUS_TONE[e.status as keyof typeof STATUS_TONE] ?? 'neutral'}
                />
              </Card>
            ))}
          </View>
        )}
      </View>
    </View>
  );
}
