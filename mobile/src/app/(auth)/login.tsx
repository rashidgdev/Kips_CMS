import { zodResolver } from '@hookform/resolvers/zod';
import { Image } from 'expo-image';
import { Redirect, router } from 'expo-router';
import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { KeyboardAvoidingView, Platform, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button, Input } from '@/components/ui';
import { ApiError } from '@/lib/api/client';
import { useAuth } from '@/lib/auth/AuthContext';
import { loginSchema, type LoginInput } from '@/lib/auth/schemas';

export default function LoginScreen() {
  const { isAuthenticated, user, login } = useAuth();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: '', password: '' },
  });

  // Already logged in (e.g. deep-linked here) - let the root gate decide where to go.
  if (isAuthenticated && !user?.must_change_password) return <Redirect href="/" />;

  const onSubmit = async (data: LoginInput) => {
    setFormError(null);
    try {
      await login(data.username, data.password);
      router.replace('/');
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        setFormError('Incorrect username or password.');
      } else {
        setFormError(error instanceof Error ? error.message : 'Could not sign in.');
      }
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <KeyboardAvoidingView className="flex-1" behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerClassName="flex-1 justify-center px-6" keyboardShouldPersistTaps="handled">
          <View className="mb-10 items-center">
            <Image
              source={require('@/assets/images/kips-logo-icon.png')}
              style={{ width: 96, height: 137 }}
              contentFit="contain"
              accessibilityLabel="KIPS College Kasur Campus"
            />
            <Text className="mt-3 text-2xl font-bold text-brand-700">KIPS CMS</Text>
            <Text className="mt-1 text-sm text-gray-500">Sign in to continue</Text>
          </View>

          <Controller
            control={control}
            name="username"
            render={({ field }) => (
              <Input
                label="Username"
                autoCapitalize="none"
                autoCorrect={false}
                value={field.value}
                onChangeText={field.onChange}
                onBlur={field.onBlur}
                error={errors.username?.message}
                returnKeyType="next"
              />
            )}
          />
          <Controller
            control={control}
            name="password"
            render={({ field }) => (
              <Input
                label="Password"
                secureTextEntry
                autoCapitalize="none"
                value={field.value}
                onChangeText={field.onChange}
                onBlur={field.onBlur}
                error={errors.password?.message}
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

          <Button label="Sign in" onPress={handleSubmit(onSubmit)} loading={isSubmitting} fullWidth />
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
