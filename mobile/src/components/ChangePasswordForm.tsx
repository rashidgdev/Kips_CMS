import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { Text, View } from 'react-native';

import { Button, Input } from '@/components/ui';
import { apiFetch } from '@/lib/api/client';
import { changePasswordSchema, type ChangePasswordInput } from '@/lib/auth/schemas';
import { applyServerErrors } from '@/lib/forms/applyServerErrors';

const FIELDS = ['old_password', 'new_password1', 'new_password2'] as const;

export function ChangePasswordForm({
  onSuccess,
  submitLabel = 'Change password',
  oldPasswordLabel = 'Current password',
}: {
  onSuccess: () => void;
  submitLabel?: string;
  oldPasswordLabel?: string;
}) {
  const [formError, setFormError] = useState<string | null>(null);
  const {
    control,
    handleSubmit,
    setError,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ChangePasswordInput>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: { old_password: '', new_password1: '', new_password2: '' },
  });

  const onSubmit = async (data: ChangePasswordInput) => {
    setFormError(null);
    try {
      await apiFetch.post('/accounts/change-password/', data);
      reset();
      onSuccess();
    } catch (error) {
      setFormError(applyServerErrors(error, setError, FIELDS));
    }
  };

  return (
    <View>
      <Controller
        control={control}
        name="old_password"
        render={({ field }) => (
          <Input
            label={oldPasswordLabel}
            secureTextEntry
            autoCapitalize="none"
            value={field.value}
            onChangeText={field.onChange}
            onBlur={field.onBlur}
            error={errors.old_password?.message}
          />
        )}
      />
      <Controller
        control={control}
        name="new_password1"
        render={({ field }) => (
          <Input
            label="New password"
            secureTextEntry
            autoCapitalize="none"
            value={field.value}
            onChangeText={field.onChange}
            onBlur={field.onBlur}
            error={errors.new_password1?.message}
          />
        )}
      />
      <Controller
        control={control}
        name="new_password2"
        render={({ field }) => (
          <Input
            label="Confirm new password"
            secureTextEntry
            autoCapitalize="none"
            value={field.value}
            onChangeText={field.onChange}
            onBlur={field.onBlur}
            error={errors.new_password2?.message}
            returnKeyType="done"
            onSubmitEditing={handleSubmit(onSubmit)}
          />
        )}
      />

      {formError && (
        <View className="mb-4 rounded-xl bg-red-50 px-3.5 py-3">
          <Text className="text-sm text-red-700">{formError}</Text>
        </View>
      )}

      <Button label={submitLabel} onPress={handleSubmit(onSubmit)} loading={isSubmitting} fullWidth />
    </View>
  );
}
