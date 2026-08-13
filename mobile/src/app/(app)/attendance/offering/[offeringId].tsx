import { zodResolver } from '@hookform/resolvers/zod';
import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { FlatList, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { z } from 'zod';

import { Button, Card, EmptyState, ErrorState, Input, LoadingState } from '@/components/ui';
import { useCreateSession, useSessions } from '@/features/attendance/api';
import { ApiError } from '@/lib/api/client';

const sessionSchema = z.object({
  date: z.string().min(1, 'Date is required (YYYY-MM-DD)'),
  start_time: z.string().min(1, 'Start time is required (HH:MM)'),
  end_time: z.string().min(1, 'End time is required (HH:MM)'),
  topic_covered: z.string(),
});
type SessionInput = z.infer<typeof sessionSchema>;

function NewSessionForm({ offeringId, onDone }: { offeringId: number; onDone: () => void }) {
  const createSession = useCreateSession(offeringId);
  const [formError, setFormError] = useState<string | null>(null);
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<SessionInput>({
    resolver: zodResolver(sessionSchema),
    defaultValues: { date: '', start_time: '', end_time: '', topic_covered: '' },
  });

  const onSubmit = async (data: SessionInput) => {
    setFormError(null);
    try {
      await createSession.mutateAsync(data);
      onDone();
    } catch (error) {
      setFormError(error instanceof ApiError ? error.message : 'Could not create the session.');
    }
  };

  return (
    <Card className="mb-4">
      <Text className="mb-3 text-base font-semibold text-gray-900">New Session</Text>
      <Controller
        control={control}
        name="date"
        render={({ field }) => (
          <Input
            label="Date"
            placeholder="2026-08-15"
            value={field.value}
            onChangeText={field.onChange}
            error={errors.date?.message}
          />
        )}
      />
      <View className="flex-row gap-3">
        <View className="flex-1">
          <Controller
            control={control}
            name="start_time"
            render={({ field }) => (
              <Input
                label="Start Time"
                placeholder="09:00"
                value={field.value}
                onChangeText={field.onChange}
                error={errors.start_time?.message}
              />
            )}
          />
        </View>
        <View className="flex-1">
          <Controller
            control={control}
            name="end_time"
            render={({ field }) => (
              <Input
                label="End Time"
                placeholder="09:45"
                value={field.value}
                onChangeText={field.onChange}
                error={errors.end_time?.message}
              />
            )}
          />
        </View>
      </View>
      <Controller
        control={control}
        name="topic_covered"
        render={({ field }) => (
          <Input
            label="Topic Covered"
            value={field.value}
            onChangeText={field.onChange}
            error={errors.topic_covered?.message}
          />
        )}
      />
      {formError && <Text className="mb-3 text-sm text-red-600">{formError}</Text>}
      <Button label="Create Session" onPress={handleSubmit(onSubmit)} loading={createSession.isPending} fullWidth />
    </Card>
  );
}

export default function OfferingSessionsScreen() {
  const { offeringId } = useLocalSearchParams<{ offeringId: string }>();
  const id = Number(offeringId);
  const [showForm, setShowForm] = useState(false);
  const { data, isPending, isError, error, refetch } = useSessions(id);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Sessions' }} />
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data}
          keyExtractor={(item) => String(item.id)}
          contentContainerClassName="px-4 py-4 gap-2"
          ListHeaderComponent={
            <>
              {showForm ? (
                <NewSessionForm offeringId={id} onDone={() => setShowForm(false)} />
              ) : (
                <View className="mb-4">
                  <Button label="+ Add Session" variant="secondary" onPress={() => setShowForm(true)} />
                </View>
              )}
            </>
          }
          ListEmptyComponent={<EmptyState title="No sessions recorded yet" />}
          renderItem={({ item }) => (
            <Card
              onPress={() =>
                router.push({ pathname: '/attendance/session/[sessionId]', params: { sessionId: String(item.id) } })
              }
            >
              <Text className="text-sm font-semibold text-gray-900">{item.date}</Text>
              <Text className="mt-0.5 text-xs text-gray-500">
                {item.start_time}–{item.end_time}
                {item.topic_covered ? ` · ${item.topic_covered}` : ''}
              </Text>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
