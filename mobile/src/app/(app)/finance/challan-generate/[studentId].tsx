import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button, Card, EmptyState, ErrorState, Input, LoadingState } from '@/components/ui';
import { useChallanGenerateOptions, useGenerateChallan } from '@/features/finance/api';
import { ApiError } from '@/lib/api/client';
import { formatCurrency } from '@/lib/format';

export default function ChallanGenerateScreen() {
  const { studentId } = useLocalSearchParams<{ studentId: string }>();
  const id = Number(studentId);
  const { data, isPending, isError, error, refetch } = useChallanGenerateOptions(id);
  const generateChallan = useGenerateChallan(id);
  const [amounts, setAmounts] = useState<Record<number, string>>({});
  const [formError, setFormError] = useState<string | null>(null);

  const toggleItem = (feeItemId: number, outstanding: number) => {
    setAmounts((prev) => {
      const next = { ...prev };
      if (feeItemId in next) {
        delete next[feeItemId];
      } else {
        next[feeItemId] = String(outstanding);
      }
      return next;
    });
  };

  const onSubmit = async () => {
    setFormError(null);
    const items = Object.entries(amounts).map(([feeItemId, amount]) => ({
      fee_item_id: Number(feeItemId),
      amount,
    }));
    if (items.length === 0) {
      setFormError('Select at least one fee item to include.');
      return;
    }
    try {
      const result = await generateChallan.mutateAsync(items);
      router.replace({ pathname: '/challans/[challanId]', params: { challanId: String(result.challan.id) } });
    } catch (error) {
      setFormError(error instanceof ApiError ? error.message : 'Could not generate the challan.');
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'Generate Challan' }} />
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <ScrollView contentContainerClassName="px-4 py-4 gap-2">
          <Text className="mb-2 text-xs text-gray-500">
            Select fee items to include. Adjust the amount for a partial (installment) payment.
          </Text>
          {data.outstanding_items.length === 0 ? (
            <EmptyState title="Nothing outstanding" message="This student has no outstanding fee items to challan." />
          ) : (
            data.outstanding_items.map(({ fee_item, outstanding }) => {
              const selected = fee_item.id in amounts;
              return (
                <Card key={fee_item.id} className={selected ? 'border-brand-300' : ''}>
                  <Pressable
                    accessibilityRole="checkbox"
                    accessibilityState={{ checked: selected }}
                    onPress={() => toggleItem(fee_item.id, outstanding)}
                    className="flex-row items-center justify-between"
                  >
                    <Text className="flex-1 text-sm font-semibold text-gray-900">{fee_item.category_label}</Text>
                    <Text className="text-xs text-gray-500">Outstanding: {formatCurrency(outstanding)}</Text>
                  </Pressable>
                  {selected && (
                    <View className="mt-2">
                      <Input
                        keyboardType="numeric"
                        value={amounts[fee_item.id]}
                        onChangeText={(text) => setAmounts((prev) => ({ ...prev, [fee_item.id]: text }))}
                      />
                    </View>
                  )}
                </Card>
              );
            })
          )}

          {formError && <Text className="mt-2 text-sm text-red-600">{formError}</Text>}
          <Button
            label="Generate Challan"
            onPress={() => void onSubmit()}
            loading={generateChallan.isPending}
            fullWidth
          />
        </ScrollView>
      )}
    </SafeAreaView>
  );
}
