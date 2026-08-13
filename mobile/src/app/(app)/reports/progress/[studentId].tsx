import { Stack, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Card, ChipPicker, ErrorState, LoadingState, StatCard } from '@/components/ui';
import { useProgressReport } from '@/features/reports/api';
import { formatPercent } from '@/lib/format';

export default function ProgressReportScreen() {
  const { studentId } = useLocalSearchParams<{ studentId: string }>();
  const id = Number(studentId);
  const [semesterId, setSemesterId] = useState<number | null>(null);
  const { data, isPending, isError, error, refetch } = useProgressReport(id, semesterId);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: data?.name ?? 'Progress Report' }} />
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <ScrollView contentContainerClassName="px-4 py-4 gap-4">
          {data.semesters.length > 0 && (
            <View>
              <Text className="mb-2 text-sm font-medium text-gray-700">Semester</Text>
              <ChipPicker
                options={data.semesters.map((s) => ({ value: s.id, label: s.label }))}
                value={semesterId ?? data.selected_semester_id ?? null}
                onChange={setSemesterId}
              />
            </View>
          )}

          {!data.report ? (
            <Card>
              <Text className="text-sm text-gray-600">No progress data available for this student yet.</Text>
            </Card>
          ) : (
            <>
              <View className="flex-row gap-3">
                <StatCard label="Attendance" value={formatPercent(data.report.attendance_overall)} />
                <StatCard label="Semester GPA" value={data.report.semester_gpa?.toFixed(2) ?? '—'} />
              </View>

              <View>
                <Text className="mb-2 text-base font-semibold text-gray-900">By Assessment Category</Text>
                <View className="gap-2">
                  {data.report.category_breakdown.map((cat) => (
                    <Card key={cat.name} className="flex-row items-center justify-between">
                      <Text className="text-sm text-gray-900">{cat.name}</Text>
                      <Text className="text-sm font-medium text-gray-700">{formatPercent(cat.percentage)}</Text>
                    </Card>
                  ))}
                </View>
              </View>

              <View>
                <Text className="mb-2 text-base font-semibold text-gray-900">Courses</Text>
                <View className="gap-2">
                  {data.report.course_rows.map((row) => (
                    <Card key={row.offering_id}>
                      <View className="flex-row items-center justify-between">
                        <Text className="flex-1 text-sm font-semibold text-gray-900">{row.course}</Text>
                        {row.grade_letter && (
                          <Text className="text-sm font-bold text-brand-700">{row.grade_letter}</Text>
                        )}
                      </View>
                      <Text className="mt-1 text-xs text-gray-500">
                        Attendance {formatPercent(row.attendance_percentage)}
                        {row.total_obtained !== null ? ` · ${row.total_obtained}/${row.total_possible} marks` : ''}
                      </Text>
                    </Card>
                  ))}
                </View>
              </View>
            </>
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}
