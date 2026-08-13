import { Redirect, router } from 'expo-router';
import { KeyboardAvoidingView, Platform, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ChangePasswordForm } from '@/components/ChangePasswordForm';
import { Button } from '@/components/ui';
import { useAuth } from '@/lib/auth/AuthContext';

export default function ChangePasswordScreen() {
  const { isAuthenticated, user, refreshMe, logout } = useAuth();

  if (!isAuthenticated) return <Redirect href="/(auth)/login" />;
  // Not forced (or already changed it this session) - nothing to do here.
  if (!user?.must_change_password) return <Redirect href="/" />;

  return (
    <SafeAreaView className="flex-1 bg-white">
      <KeyboardAvoidingView className="flex-1" behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerClassName="flex-1 justify-center px-6" keyboardShouldPersistTaps="handled">
          <View className="mb-6">
            <Text className="text-2xl font-bold text-gray-900">Set a new password</Text>
            <Text className="mt-1 text-sm text-gray-500">
              Your account was created with a temporary password. Choose your own before continuing.
            </Text>
          </View>

          <ChangePasswordForm
            submitLabel="Save and continue"
            oldPasswordLabel="Current (temporary) password"
            onSuccess={async () => {
              await refreshMe();
              router.replace('/');
            }}
          />

          <View className="mt-3">
            <Button label="Log out instead" variant="ghost" onPress={() => void logout()} />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
