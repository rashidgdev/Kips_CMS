import Ionicons from '@expo/vector-icons/Ionicons';
import { Image } from 'expo-image';
import { router, Stack } from 'expo-router';
import { useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ChangePasswordForm } from '@/components/ChangePasswordForm';
import { Badge, Card } from '@/components/ui';
import { useAuth } from '@/lib/auth/AuthContext';
import { useUpdatePhoto } from '@/lib/auth/useUpdatePhoto';

function ProfileField({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null;
  return (
    <View className="border-t border-gray-100 py-2.5 first:border-t-0">
      <Text className="text-xs text-gray-500">{label}</Text>
      <Text className="mt-0.5 text-base text-gray-900">{value}</Text>
    </View>
  );
}

export default function ProfileScreen() {
  const { user } = useAuth();
  const updatePhoto = useUpdatePhoto();
  const [showChangePassword, setShowChangePassword] = useState(false);

  if (!user) return null;

  const profile = user.profile;
  const roleFields: { label: string; value: string | null | undefined }[] = [];
  if (profile) {
    if ('roll_number' in profile) {
      roleFields.push(
        { label: 'Roll Number', value: profile.roll_number },
        { label: 'Program', value: profile.program },
        { label: 'Current Semester', value: profile.current_semester },
      );
    } else if ('designation' in profile) {
      roleFields.push(
        { label: 'Employee ID', value: profile.employee_id },
        { label: 'Department', value: profile.department },
        { label: 'Designation', value: profile.designation },
      );
    } else if ('employee_id' in profile) {
      roleFields.push({ label: 'Employee ID', value: profile.employee_id });
    }
  }

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'My Profile' }} />
      <KeyboardAvoidingView className="flex-1" behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerClassName="px-4 py-4">
          <Card className="mb-4 items-center">
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Change profile photo"
              onPress={() => updatePhoto.mutate()}
              disabled={updatePhoto.isPending}
              className="relative"
            >
              {user.photo_url ? (
                <Image source={{ uri: user.photo_url }} className="h-20 w-20 rounded-full bg-gray-200" />
              ) : (
                <View className="h-20 w-20 items-center justify-center rounded-full bg-brand-100">
                  <Ionicons name="person" size={36} color="#1d4ed8" />
                </View>
              )}
              <View className="absolute -bottom-1 -right-1 rounded-full bg-brand-700 p-1.5">
                <Ionicons name="camera" size={14} color="#fff" />
              </View>
            </Pressable>
            {updatePhoto.error && <Text className="mt-2 text-xs text-red-600">{updatePhoto.error.message}</Text>}

            <Text className="mt-3 text-lg font-bold text-gray-900">{user.full_name}</Text>
            <Text className="text-sm text-gray-500">@{user.username}</Text>
            <View className="mt-2">
              <Badge label={user.role_display} tone="brand" />
            </View>
          </Card>

          <Card className="mb-4">
            <ProfileField label="Email" value={user.email} />
            <ProfileField label="Phone" value={user.phone_number} />
            {roleFields.map((f) => (
              <ProfileField key={f.label} label={f.label} value={f.value} />
            ))}
          </Card>

          <Card>
            <Pressable
              accessibilityRole="button"
              onPress={() => setShowChangePassword((v) => !v)}
              className="flex-row items-center justify-between"
            >
              <Text className="text-base font-semibold text-gray-900">Change password</Text>
              <Ionicons name={showChangePassword ? 'chevron-up' : 'chevron-down'} size={18} color="#6b7280" />
            </Pressable>
            {showChangePassword && (
              <View className="mt-4">
                <ChangePasswordForm
                  submitLabel="Update password"
                  onSuccess={() => {
                    setShowChangePassword(false);
                    router.back();
                  }}
                />
              </View>
            )}
          </Card>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
