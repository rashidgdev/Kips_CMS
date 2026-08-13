import { useState } from 'react';
import { Alert, FlatList, Pressable, Switch, Text, View } from 'react-native';

import { Button, Card, ChipPicker, EmptyState, ErrorState, Input, LoadingState } from '@/components/ui';
import { ApiError } from '@/lib/api/client';

import { useSimpleCrudCreate, useSimpleCrudDelete, useSimpleCrudList, useSimpleCrudUpdate } from './simpleCrud';

export type FieldConfig =
  | { key: string; label: string; type: 'text' | 'number' | 'date'; required?: boolean }
  | { key: string; label: string; type: 'boolean' }
  | { key: string; label: string; type: 'picker'; options: { value: number | string; label: string }[]; required?: boolean };

type Row = Record<string, unknown> & { id: number };

function emptyValues(fields: FieldConfig[]): Record<string, unknown> {
  return Object.fromEntries(
    fields.map((f) => [f.key, f.type === 'boolean' ? false : f.type === 'picker' ? null : '']),
  );
}

function RecordForm({
  fields,
  initial,
  onSubmit,
  onCancel,
  submitting,
  submitError,
}: {
  fields: FieldConfig[];
  initial: Record<string, unknown>;
  onSubmit: (values: Record<string, unknown>) => void;
  onCancel: () => void;
  submitting: boolean;
  submitError: string | null;
}) {
  const [values, setValues] = useState(initial);

  return (
    <Card className="mb-4">
      {fields.map((field) => (
        <View key={field.key} className="mb-3">
          <Text className="mb-1.5 text-sm font-medium text-gray-700">
            {field.label}
            {'required' in field && field.required && <Text className="text-red-600"> *</Text>}
          </Text>
          {field.type === 'boolean' ? (
            <Switch
              value={Boolean(values[field.key])}
              onValueChange={(v) => setValues((prev) => ({ ...prev, [field.key]: v }))}
            />
          ) : field.type === 'picker' ? (
            <ChipPicker
              options={field.options}
              value={values[field.key] as string | number | null}
              onChange={(v) => setValues((prev) => ({ ...prev, [field.key]: v }))}
            />
          ) : (
            <Input
              keyboardType={field.type === 'number' ? 'numeric' : 'default'}
              placeholder={field.type === 'date' ? 'YYYY-MM-DD' : undefined}
              value={String(values[field.key] ?? '')}
              onChangeText={(text) => setValues((prev) => ({ ...prev, [field.key]: text }))}
            />
          )}
        </View>
      ))}
      {submitError && <Text className="mb-3 text-sm text-red-600">{submitError}</Text>}
      <View className="flex-row gap-2">
        <View className="flex-1">
          <Button label="Save" onPress={() => onSubmit(values)} loading={submitting} fullWidth />
        </View>
        <View className="flex-1">
          <Button label="Cancel" variant="secondary" onPress={onCancel} fullWidth />
        </View>
      </View>
    </Card>
  );
}

export function SimpleCrudScreen<T extends Row>({
  basePath,
  fields,
  renderItemLabel,
  canDelete = true,
}: {
  basePath: string;
  fields: FieldConfig[];
  renderItemLabel: (item: T) => { title: string; subtitle?: string };
  canDelete?: boolean;
}) {
  const { data, isPending, isError, error, refetch } = useSimpleCrudList<T>(basePath);
  const create = useSimpleCrudCreate<T>(basePath);
  const update = useSimpleCrudUpdate<T>(basePath);
  const remove = useSimpleCrudDelete(basePath);

  const [mode, setMode] = useState<'closed' | 'create' | number>('closed');
  const [formError, setFormError] = useState<string | null>(null);

  if (isPending) return <LoadingState />;
  if (isError) return <ErrorState error={error} onRetry={() => void refetch()} />;

  const editingItem = typeof mode === 'number' ? data.results.find((r) => r.id === mode) : null;

  const onCreate = (values: Record<string, unknown>) => {
    setFormError(null);
    create.mutate(values, {
      onSuccess: () => setMode('closed'),
      onError: (err) => setFormError(err instanceof ApiError ? err.message : 'Could not create.'),
    });
  };

  const onUpdate = (id: number, values: Record<string, unknown>) => {
    setFormError(null);
    update.mutate(
      { id, body: values },
      {
        onSuccess: () => setMode('closed'),
        onError: (err) => setFormError(err instanceof ApiError ? err.message : 'Could not save.'),
      },
    );
  };

  const onDelete = (id: number) => {
    Alert.alert('Delete', 'Delete this record?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: () =>
          remove.mutate(id, {
            onSuccess: () => setMode('closed'),
            onError: () => Alert.alert('Could not delete', 'This record may be in use elsewhere.'),
          }),
      },
    ]);
  };

  return (
    <FlatList
      data={data.results}
      keyExtractor={(item) => String(item.id)}
      contentContainerClassName="px-4 py-4 gap-2"
      ListHeaderComponent={
        <>
          {mode === 'create' && (
            <RecordForm
              fields={fields}
              initial={emptyValues(fields)}
              onSubmit={onCreate}
              onCancel={() => setMode('closed')}
              submitting={create.isPending}
              submitError={formError}
            />
          )}
          {mode === 'closed' && (
            <View className="mb-4">
              <Button label="+ Add" variant="secondary" onPress={() => setMode('create')} />
            </View>
          )}
        </>
      }
      ListEmptyComponent={<EmptyState title="Nothing here yet" />}
      renderItem={({ item }) => {
        const { title, subtitle } = renderItemLabel(item);
        if (editingItem && editingItem.id === item.id) {
          return (
            <RecordForm
              fields={fields}
              initial={item}
              onSubmit={(values) => onUpdate(item.id, values)}
              onCancel={() => setMode('closed')}
              submitting={update.isPending}
              submitError={formError}
            />
          );
        }
        return (
          <Card>
            <View className="flex-row items-center justify-between">
              <Pressable accessibilityRole="button" onPress={() => setMode(item.id)} className="flex-1">
                <Text className="text-sm font-semibold text-gray-900">{title}</Text>
                {subtitle && <Text className="mt-0.5 text-xs text-gray-500">{subtitle}</Text>}
              </Pressable>
              {canDelete && (
                <Pressable accessibilityRole="button" onPress={() => onDelete(item.id)} className="px-2 py-1">
                  <Text className="text-xs font-medium text-red-600">Delete</Text>
                </Pressable>
              )}
            </View>
          </Card>
        );
      }}
    />
  );
}
