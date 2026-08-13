import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button, ChipPicker, LoadingState } from '@/components/ui';
import { useOfferingsForSemester, useRooms, useScheduleEntry, useTimeSlots } from '@/features/timetable/api';
import { ApiError } from '@/lib/api/client';

export default function ScheduleClassScreen() {
  const { semesterId } = useLocalSearchParams<{ semesterId: string }>();
  const id = Number(semesterId);

  const { data: offerings, isPending: offeringsPending } = useOfferingsForSemester(id);
  const { data: rooms, isPending: roomsPending } = useRooms();
  const { data: timeSlots, isPending: timeSlotsPending } = useTimeSlots();
  const scheduleEntry = useScheduleEntry(id);

  const [offeringId, setOfferingId] = useState<number | null>(null);
  const [roomId, setRoomId] = useState<number | null>(null);
  const [timeSlotId, setTimeSlotId] = useState<number | null>(null);
  const [errors, setErrors] = useState<string[]>([]);

  const isLoading = offeringsPending || roomsPending || timeSlotsPending;

  const onSubmit = async () => {
    setErrors([]);
    if (!offeringId || !roomId || !timeSlotId) {
      setErrors(['Select a course offering, room, and time slot.']);
      return;
    }
    try {
      await scheduleEntry.mutateAsync({ course_offering: offeringId, room: roomId, time_slot: timeSlotId });
      router.back();
    } catch (error) {
      if (error instanceof ApiError && error.data && typeof error.data === 'object' && 'errors' in error.data) {
        const apiErrors = (error.data as { errors: unknown }).errors;
        setErrors(Array.isArray(apiErrors) ? apiErrors.filter((e): e is string => typeof e === 'string') : [error.message]);
      } else {
        setErrors([error instanceof Error ? error.message : 'Could not schedule this class.']);
      }
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Schedule Class' }} />
      {isLoading ? (
        <LoadingState />
      ) : (
        <ScrollView contentContainerClassName="px-4 py-4 gap-5">
          <View>
            <Text className="mb-2 text-sm font-medium text-gray-700">Course Offering</Text>
            <ChipPicker
              options={(offerings ?? []).map((o) => ({
                value: o.id,
                label: `${o.course_label} (${o.section})`,
              }))}
              value={offeringId}
              onChange={setOfferingId}
            />
          </View>

          <View>
            <Text className="mb-2 text-sm font-medium text-gray-700">Room</Text>
            <ChipPicker
              options={(rooms?.results ?? []).map((r) => ({ value: r.id, label: r.name }))}
              value={roomId}
              onChange={setRoomId}
            />
          </View>

          <View>
            <Text className="mb-2 text-sm font-medium text-gray-700">Time Slot</Text>
            <ChipPicker
              options={(timeSlots?.results ?? []).map((t) => ({
                value: t.id,
                label: `${t.day_of_week_display.slice(0, 3)} ${t.start_time_display}${t.label ? ` · ${t.label}` : ''}`,
              }))}
              value={timeSlotId}
              onChange={setTimeSlotId}
            />
          </View>

          {errors.length > 0 && (
            <View className="rounded-xl bg-red-50 px-3.5 py-3">
              {errors.map((msg, i) => (
                <Text key={i} className="text-sm text-red-700">
                  {msg}
                </Text>
              ))}
            </View>
          )}

          <Button label="Schedule Class" onPress={() => void onSubmit()} loading={scheduleEntry.isPending} fullWidth />
        </ScrollView>
      )}
    </SafeAreaView>
  );
}
