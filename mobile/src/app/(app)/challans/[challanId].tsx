import { Stack, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { Alert, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Button, Card, ChipPicker, ErrorState, LoadingState } from '@/components/ui';
import {
  useCancelChallan,
  useChallanDetail,
  useRecordChallanPayment,
} from '@/features/finance/api';
import { useAuth } from '@/lib/auth/AuthContext';
import { formatCurrency } from '@/lib/format';
import { useDownloadPdf } from '@/lib/pdf';

const STATUS_TONE = { paid: 'success', overdue: 'danger', unpaid: 'neutral', cancelled: 'neutral' } as const;

const PAYMENT_METHODS = [
  { value: 'cash', label: 'Cash' },
  { value: 'bank_transfer', label: 'Bank Transfer' },
  { value: 'cheque', label: 'Cheque' },
  { value: 'online', label: 'Online' },
];

export default function ChallanDetailScreen() {
  const { challanId } = useLocalSearchParams<{ challanId: string }>();
  const id = Number(challanId);
  const { user } = useAuth();
  const isStaff = user?.role === 'accountant' || user?.role === 'admin';

  const { data, isPending, isError, error, refetch } = useChallanDetail(id);
  const recordPayment = useRecordChallanPayment(id);
  const cancelChallan = useCancelChallan(id);
  const download = useDownloadPdf();
  const [paymentMethod, setPaymentMethod] = useState('cash');

  const onRecordPayment = () => {
    recordPayment.mutate(
      { payment_date: new Date().toISOString().slice(0, 10), payment_method: paymentMethod },
      { onError: (err) => Alert.alert('Could not record payment', err.message) },
    );
  };

  const onCancel = () => {
    Alert.alert('Cancel challan', 'This cannot be undone.', [
      { text: 'Back', style: 'cancel' },
      {
        text: 'Cancel Challan',
        style: 'destructive',
        onPress: () => cancelChallan.mutate(undefined, { onError: (err) => Alert.alert('Could not cancel', err.message) }),
      },
    ]);
  };

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: data?.challan.challan_number ?? 'Challan' }} />
      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <ScrollView contentContainerClassName="px-4 py-4 gap-4">
          <Card>
            <View className="flex-row items-center justify-between">
              <Text className="text-base font-bold text-gray-900">{data.challan.challan_number}</Text>
              <Badge label={data.challan.status} tone={STATUS_TONE[data.challan.status]} />
            </View>
            <Text className="mt-1 text-xs text-gray-500">{data.challan.student_label}</Text>
            <Text className="mt-1 text-xs text-gray-500">
              Issued {data.challan.issue_date} · Due {data.challan.due_date}
            </Text>
            <Text className="mt-3 text-2xl font-bold text-gray-900">{formatCurrency(data.challan.total_amount)}</Text>
          </Card>

          <View>
            <Text className="mb-2 text-base font-semibold text-gray-900">Line Items</Text>
            <View className="gap-2">
              {data.lines.map((line) => (
                <Card key={line.id} className="flex-row items-center justify-between">
                  <Text className="text-sm text-gray-900">{line.category}</Text>
                  <Text className="text-sm font-medium text-gray-700">{formatCurrency(line.amount)}</Text>
                </Card>
              ))}
            </View>
          </View>

          <Button
            label="Download PDF"
            variant="secondary"
            loading={download.isPending}
            onPress={() => download.mutate({ path: data.pdf_url, filename: `${data.challan.challan_number}.pdf` })}
          />
          {download.isError && <Text className="text-xs text-red-600">{download.error.message}</Text>}

          {isStaff && data.challan.status !== 'paid' && data.challan.status !== 'cancelled' && (
            <View className="gap-3 border-t border-gray-200 pt-4">
              <Text className="text-base font-semibold text-gray-900">Record Payment</Text>
              <ChipPicker options={PAYMENT_METHODS} value={paymentMethod} onChange={setPaymentMethod} />
              <Button label="Mark as Paid" onPress={onRecordPayment} loading={recordPayment.isPending} fullWidth />
              <Button label="Cancel Challan" variant="danger" onPress={onCancel} loading={cancelChallan.isPending} />
            </View>
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}
