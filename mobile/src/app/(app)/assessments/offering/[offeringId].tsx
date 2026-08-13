import { zodResolver } from '@hookform/resolvers/zod';
import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { FlatList, Pressable, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { z } from 'zod';

import { Badge, Button, Card, EmptyState, ErrorState, Input, LoadingState } from '@/components/ui';
import { useAssessments, useCategoryOptions, useCreateAssessment } from '@/features/assessments/api';
import { ApiError } from '@/lib/api/client';

const assessmentSchema = z.object({
  category: z.number({ error: 'Choose a category' }).min(1, 'Choose a category'),
  title: z.string().min(1, 'Title is required'),
  total_marks: z.string().min(1, 'Total marks is required'),
  weight_percent: z.string().min(1, 'Weight % is required'),
  date: z.string().min(1, 'Date is required (YYYY-MM-DD)'),
});
type AssessmentInput = z.infer<typeof assessmentSchema>;

function NewAssessmentForm({ offeringId, onDone }: { offeringId: number; onDone: () => void }) {
  const { data: categories } = useCategoryOptions();
  const createAssessment = useCreateAssessment(offeringId);
  const [formError, setFormError] = useState<string | null>(null);
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<AssessmentInput>({
    resolver: zodResolver(assessmentSchema),
    defaultValues: { category: 0, title: '', total_marks: '', weight_percent: '', date: '' },
  });

  const onSubmit = async (data: AssessmentInput) => {
    setFormError(null);
    try {
      await createAssessment.mutateAsync({
        category: data.category,
        title: data.title,
        total_marks: Number(data.total_marks),
        weight_percent: Number(data.weight_percent),
        date: data.date,
      });
      onDone();
    } catch (error) {
      setFormError(error instanceof ApiError ? error.message : 'Could not create the assessment.');
    }
  };

  return (
    <Card className="mb-4">
      <Text className="mb-3 text-base font-semibold text-gray-900">New Assessment</Text>

      <Text className="mb-1.5 text-sm font-medium text-gray-700">
        Category<Text className="text-red-600"> *</Text>
      </Text>
      <Controller
        control={control}
        name="category"
        render={({ field }) => (
          <View className="mb-1 flex-row flex-wrap gap-2">
            {(categories ?? []).map((cat) => (
              <Pressable
                key={cat.id}
                accessibilityRole="button"
                accessibilityState={{ selected: field.value === cat.id }}
                onPress={() => field.onChange(cat.id)}
                className={`rounded-full border px-3 py-1.5 ${
                  field.value === cat.id ? 'border-brand-700 bg-brand-700' : 'border-gray-300 bg-white'
                }`}
              >
                <Text className={`text-sm ${field.value === cat.id ? 'text-white' : 'text-gray-700'}`}>
                  {cat.name}
                </Text>
              </Pressable>
            ))}
          </View>
        )}
      />
      {errors.category && <Text className="mb-3 text-sm text-red-600">{errors.category.message}</Text>}

      <Controller
        control={control}
        name="title"
        render={({ field }) => (
          <Input label="Title" value={field.value} onChangeText={field.onChange} error={errors.title?.message} />
        )}
      />
      <View className="flex-row gap-3">
        <View className="flex-1">
          <Controller
            control={control}
            name="total_marks"
            render={({ field }) => (
              <Input
                label="Total Marks"
                keyboardType="numeric"
                value={field.value}
                onChangeText={field.onChange}
                error={errors.total_marks?.message}
              />
            )}
          />
        </View>
        <View className="flex-1">
          <Controller
            control={control}
            name="weight_percent"
            render={({ field }) => (
              <Input
                label="Weight %"
                keyboardType="numeric"
                value={field.value}
                onChangeText={field.onChange}
                error={errors.weight_percent?.message}
              />
            )}
          />
        </View>
      </View>
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

      {formError && <Text className="mb-3 text-sm text-red-600">{formError}</Text>}
      <Button label="Create Assessment" onPress={handleSubmit(onSubmit)} loading={createAssessment.isPending} fullWidth />
    </Card>
  );
}

export default function OfferingAssessmentsScreen() {
  const { offeringId } = useLocalSearchParams<{ offeringId: string }>();
  const id = Number(offeringId);
  const [showForm, setShowForm] = useState(false);
  const { data, isPending, isError, error, refetch } = useAssessments(id);

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Assessments' }} />
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
                <NewAssessmentForm offeringId={id} onDone={() => setShowForm(false)} />
              ) : (
                <View className="mb-4">
                  <Button label="+ Add Assessment" variant="secondary" onPress={() => setShowForm(true)} />
                </View>
              )}
            </>
          }
          ListEmptyComponent={<EmptyState title="No assessments created yet" />}
          renderItem={({ item }) => (
            <Card
              onPress={() =>
                router.push({ pathname: '/assessments/marks/[assessmentId]', params: { assessmentId: String(item.id) } })
              }
            >
              <View className="flex-row items-center justify-between">
                <Text className="text-sm font-semibold text-gray-900">{item.title}</Text>
                <Badge label={item.category_label} tone="brand" />
              </View>
              <Text className="mt-0.5 text-xs text-gray-500">
                {item.date} · {item.total_marks} marks · {item.weight_percent}% weight
              </Text>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
