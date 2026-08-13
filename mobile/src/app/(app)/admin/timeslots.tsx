import { Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

import type { FieldConfig } from '@/features/admin/SimpleCrudScreen';
import { SimpleCrudScreen } from '@/features/admin/SimpleCrudScreen';

type TimeSlot = {
  id: number; day_of_week: number; start_time: string; end_time: string; label: string;
  day_of_week_display: string; start_time_display: string; end_time_display: string;
};

const DAYS = [
  { value: 1, label: 'Mon' }, { value: 2, label: 'Tue' }, { value: 3, label: 'Wed' },
  { value: 4, label: 'Thu' }, { value: 5, label: 'Fri' }, { value: 6, label: 'Sat' },
];

const fields: FieldConfig[] = [
  { key: 'day_of_week', label: 'Day', type: 'picker', required: true, options: DAYS },
  { key: 'start_time', label: 'Start Time (HH:MM)', type: 'text', required: true },
  { key: 'end_time', label: 'End Time (HH:MM)', type: 'text', required: true },
  { key: 'label', label: 'Label', type: 'text' },
];

export default function TimeSlotsScreen() {
  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Time Slots' }} />
      <SimpleCrudScreen<TimeSlot>
        basePath="/timetable/timeslots/"
        fields={fields}
        renderItemLabel={(item) => ({
          title: `${item.day_of_week_display} · ${item.start_time_display}-${item.end_time_display}`,
          subtitle: item.label || undefined,
        })}
      />
    </SafeAreaView>
  );
}
