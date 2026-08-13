import { useMemo, useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';

import { Card, EmptyState } from '@/components/ui';

import type { Grid } from './types';

/**
 * Renders one day at a time (day chips + a vertical list of periods) rather
 * than a cramped N-day-wide table - an explicit mobile-UX adaptation of the
 * web's full grid table, which fits comfortably on a desktop screen but not
 * a phone. Break rows apply to every day identically (see build_grid() on
 * the server) so they render the same regardless of which day is selected.
 */
export function DayGrid({
  grid,
  renderCellExtra,
  onCellPress,
}: {
  grid: Grid;
  renderCellExtra?: (entryId: number) => React.ReactNode;
  onCellPress?: (entryId: number) => void;
}) {
  const todayIso = new Date().getDay() === 0 ? 7 : new Date().getDay(); // JS: Sun=0 -> ISO Sun=7
  const defaultDay = grid.days.find((d) => d.value === todayIso)?.value ?? grid.days[0]?.value ?? 1;
  const [selectedDay, setSelectedDay] = useState(defaultDay);

  const rowsForDay = useMemo(() => {
    return grid.rows.map((row) => {
      if (row.type === 'break') return row;
      const cell = row.cells.find((c) => c.day === selectedDay);
      return { type: 'period' as const, start_time: row.start_time, end_time: row.end_time, label: row.label, cell };
    });
  }, [grid.rows, selectedDay]);

  if (grid.days.length === 0) {
    return <EmptyState title="No timetable data" message="Time slots haven't been set up yet." />;
  }

  return (
    <View className="flex-1">
      <ScrollView horizontal showsHorizontalScrollIndicator={false} className="mb-3 max-h-12 grow-0">
        <View className="flex-row gap-2 px-4">
          {grid.days.map((day) => {
            const selected = day.value === selectedDay;
            return (
              <Pressable
                key={day.value}
                accessibilityRole="button"
                accessibilityState={{ selected }}
                onPress={() => setSelectedDay(day.value)}
                className={`rounded-full border px-4 py-2 ${
                  selected ? 'border-brand-700 bg-brand-700' : 'border-gray-300 bg-white'
                }`}
              >
                <Text className={`text-sm font-medium ${selected ? 'text-white' : 'text-gray-700'}`}>
                  {day.label.slice(0, 3)}
                </Text>
              </Pressable>
            );
          })}
        </View>
      </ScrollView>

      <ScrollView contentContainerClassName="px-4 pb-4 gap-2">
        {rowsForDay.length === 0 && <EmptyState title="No periods configured" />}
        {rowsForDay.map((row, index) =>
          row.type === 'break' ? (
            <View key={`break-${index}`} className="rounded-xl bg-amber-50 px-3.5 py-2.5">
              <Text className="text-xs font-medium text-amber-800">
                Break · {row.start_time.slice(0, 5)}–{row.end_time.slice(0, 5)} ({row.duration_minutes} min)
              </Text>
            </View>
          ) : row.cell?.entry_id ? (
            <Card
              key={`period-${index}`}
              onPress={onCellPress ? () => onCellPress(row.cell!.entry_id!) : undefined}
            >
              <View className="flex-row items-center justify-between">
                <Text className="text-xs font-medium text-gray-500">
                  {row.start_time.slice(0, 5)}–{row.end_time.slice(0, 5)}
                </Text>
                {renderCellExtra?.(row.cell.entry_id)}
              </View>
              <Text className="mt-1 text-sm font-semibold text-gray-900">{row.cell.course}</Text>
              <Text className="mt-0.5 text-xs text-gray-500">
                {row.cell.teacher} · {row.cell.room}
              </Text>
            </Card>
          ) : (
            <View key={`period-${index}`} className="rounded-xl border border-dashed border-gray-200 px-3.5 py-3">
              <Text className="text-xs font-medium text-gray-400">
                {row.start_time.slice(0, 5)}–{row.end_time.slice(0, 5)} · Free
              </Text>
            </View>
          ),
        )}
      </ScrollView>
    </View>
  );
}
