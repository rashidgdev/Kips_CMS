import { Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';

import type { FieldConfig } from '@/features/admin/SimpleCrudScreen';
import { SimpleCrudScreen } from '@/features/admin/SimpleCrudScreen';

type Room = { id: number; name: string; building: string; capacity: number; room_type: string };

const ROOM_TYPES = [
  { value: 'classroom', label: 'Classroom' },
  { value: 'lab', label: 'Lab' },
];

const fields: FieldConfig[] = [
  { key: 'name', label: 'Name', type: 'text', required: true },
  { key: 'building', label: 'Building', type: 'text' },
  { key: 'capacity', label: 'Capacity', type: 'number' },
  { key: 'room_type', label: 'Type', type: 'picker', options: ROOM_TYPES },
];

export default function RoomsScreen() {
  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Rooms' }} />
      <SimpleCrudScreen<Room>
        basePath="/timetable/rooms/"
        fields={fields}
        renderItemLabel={(item) => ({ title: item.name, subtitle: `${item.building} · Capacity ${item.capacity}` })}
      />
    </SafeAreaView>
  );
}
