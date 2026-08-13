import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button, ChipPicker, Input } from '@/components/ui';
import { useRecordPayment } from '@/features/finance/api';
import { applyServerErrors } from '@/lib/forms/applyServerErrors';

const PAYMENT_METHODS = [
  { value: 'cash', label: 'Cash' },
  { value: 'bank_transfer', label: 'Bank Transfer' },
  { value: 'cheque', label: 'Cheque' },
  { value: 'online', label: 'Online' },
];

type PaymentInput = { amount_paid: string; payment_date: string };

export default function RecordPaymentScreen() {
  const { itemId, studentId } = useLocalSearchParams<{ itemId: string; studentId: string }>();
  const recordPayment = useRecordPayment(Number(itemId), Number(studentId));
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [formError, setFormError] = useState<string | null>(null);
  const {
    control,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<PaymentInput>({ defaultValues: { amount_paid: '', payment_date: new Date().toISOString().slice(0, 10) } });

  const onSubmit = async (data: PaymentInput) => {
    setFormError(null);
    try {
      await recordPayment.mutateAsync({ ...data, payment_method: paymentMethod });
      router.back();
    } catch (error) {
      setFormError(applyServerErrors(error, setError, ['amount_paid', 'payment_date', 'payment_method']));
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ headerShown: true, title: 'Record Payment' }} />
      <View className="px-4 py-4">
        <Controller
          control={control}
          name="amount_paid"
          rules={{ required: 'Amount is required' }}
          render={({ field }) => (
            <Input
              label="Amount"
              keyboardType="numeric"
              value={field.value}
              onChangeText={field.onChange}
              error={errors.amount_paid?.message}
            />
          )}
        />
        <Controller
          control={control}
          name="payment_date"
          rules={{ required: 'Date is required' }}
          render={({ field }) => (
            <Input label="Payment Date" value={field.value} onChangeText={field.onChange} error={errors.payment_date?.message} />
          )}
        />

        <Text className="mb-2 text-sm font-medium text-gray-700">Payment Method</Text>
        <View className="mb-4">
          <ChipPicker options={PAYMENT_METHODS} value={paymentMethod} onChange={setPaymentMethod} />
        </View>

        {formError && <Text className="mb-3 text-sm text-red-600">{formError}</Text>}
        <Button label="Record Payment" onPress={handleSubmit(onSubmit)} loading={recordPayment.isPending} fullWidth />
      </View>
    </SafeAreaView>
  );
}
