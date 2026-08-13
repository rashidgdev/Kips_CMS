import { Text, View } from 'react-native';

import { Card, EmptyState } from '@/components/ui';

import type { TeacherDashboard as TeacherDashboardData } from './types';

export function TeacherDashboard({ data }: { data: TeacherDashboardData }) {
  return (
    <View className="gap-4">
      {data.department && (
        <Card>
          <Text className="text-xs text-gray-500">Department</Text>
          <Text className="mt-0.5 text-base font-semibold text-gray-900">{data.department}</Text>
        </Card>
      )}

      <View>
        <Text className="mb-2 text-base font-semibold text-gray-900">Today&apos;s Classes</Text>
        {data.todays_classes.length === 0 ? (
          <EmptyState title="No classes today" />
        ) : (
          <View className="gap-2">
            {data.todays_classes.map((c) => (
              <Card key={c.id} className="flex-row items-center justify-between">
                <View className="flex-1">
                  <Text className="text-sm font-semibold text-gray-900">{c.course}</Text>
                  <Text className="mt-0.5 text-xs text-gray-500">
                    {c.room} · {c.start_time}–{c.end_time}
                  </Text>
                </View>
              </Card>
            ))}
          </View>
        )}
      </View>

      <View>
        <Text className="mb-2 text-base font-semibold text-gray-900">My Course Offerings</Text>
        {data.offerings.length === 0 ? (
          <EmptyState title="No course offerings assigned" />
        ) : (
          <View className="gap-2">
            {data.offerings.map((o) => (
              <Card key={o.id}>
                <Text className="text-sm font-semibold text-gray-900">{o.course}</Text>
                <Text className="mt-0.5 text-xs text-gray-500">
                  {o.semester} · Section {o.section}
                </Text>
              </Card>
            ))}
          </View>
        )}
      </View>
    </View>
  );
}
