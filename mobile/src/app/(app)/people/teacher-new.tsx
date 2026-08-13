import { Stack, useRouter } from 'expo-router';
import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { KeyboardAvoidingView, Platform, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { PhotoPickerField } from '@/components/PhotoPickerField';
import { TempPasswordCard } from '@/components/TempPasswordCard';
import { Button, ChipPicker, Input } from '@/components/ui';
import { useSimpleCrudList } from '@/features/admin/simpleCrud';
import { useCreatePerson } from '@/features/people/api';
import type { CreatePersonResult } from '@/features/people/types';
import { applyServerErrors } from '@/lib/forms/applyServerErrors';

type Department = { id: number; name: string; code: string };

type TeacherInput = {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  employee_id: string;
  designation: string;
  qualification: string;
  joining_date: string;
  per_lecture_rate: string;
};

const FIELDS = [
  'username', 'first_name', 'last_name', 'email', 'phone_number', 'photo', 'role',
  'employee_id', 'department', 'designation', 'qualification', 'joining_date', 'per_lecture_rate',
];

const ROLE_OPTIONS = [
  { value: 'teacher', label: 'Teacher' },
  { value: 'hod', label: 'Head of Department' },
];

export default function TeacherCreateScreen() {
  const router = useRouter();
  const { data: departments } = useSimpleCrudList<Department>('/accounts/departments/');
  const createTeacher = useCreatePerson('teachers');

  const [role, setRole] = useState('teacher');
  const [departmentId, setDepartmentId] = useState<number | null>(null);
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [result, setResult] = useState<CreatePersonResult | null>(null);

  const {
    control,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<TeacherInput>({
    defaultValues: {
      username: '', first_name: '', last_name: '', email: '', phone_number: '',
      employee_id: '', designation: '', qualification: '', joining_date: '', per_lecture_rate: '0',
    },
  });

  if (result) {
    return (
      <SafeAreaView className="flex-1 bg-gray-50">
        <Stack.Screen options={{ headerShown: true, title: 'Teacher Added' }} />
        <View className="px-4 py-4">
          <TempPasswordCard username={result.username} tempPassword={result.temp_password} onDone={() => router.back()} />
        </View>
      </SafeAreaView>
    );
  }

  const onSubmit = async (data: TeacherInput) => {
    setFormError(null);
    if (!departmentId) {
      setFormError('Select a department.');
      return;
    }
    try {
      const res = await createTeacher.mutateAsync({
        fields: { ...data, role, department: departmentId },
        photoUri,
      });
      setResult(res);
    } catch (error) {
      setFormError(applyServerErrors(error, setError, FIELDS));
    }
  };

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ headerShown: true, title: 'Add Teacher' }} />
      <KeyboardAvoidingView className="flex-1" behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerClassName="px-4 py-4" keyboardShouldPersistTaps="handled">
          <Controller control={control} name="username" render={({ field }) => (
            <Input label="Username" autoCapitalize="none" value={field.value} onChangeText={field.onChange} error={errors.username?.message} />
          )} />
          <Controller control={control} name="first_name" render={({ field }) => (
            <Input label="First Name" value={field.value} onChangeText={field.onChange} error={errors.first_name?.message} />
          )} />
          <Controller control={control} name="last_name" render={({ field }) => (
            <Input label="Last Name" value={field.value} onChangeText={field.onChange} error={errors.last_name?.message} />
          )} />
          <Controller control={control} name="email" render={({ field }) => (
            <Input label="Email" autoCapitalize="none" keyboardType="email-address" value={field.value} onChangeText={field.onChange} error={errors.email?.message} />
          )} />
          <Controller control={control} name="phone_number" render={({ field }) => (
            <Input label="Phone Number" value={field.value} onChangeText={field.onChange} error={errors.phone_number?.message} />
          )} />
          <PhotoPickerField uri={photoUri} onChange={setPhotoUri} />

          <Text className="mb-2 text-sm font-medium text-gray-700">Role</Text>
          <View className="mb-4">
            <ChipPicker options={ROLE_OPTIONS} value={role} onChange={setRole} />
          </View>

          <Controller control={control} name="employee_id" render={({ field }) => (
            <Input label="Employee ID" value={field.value} onChangeText={field.onChange} error={errors.employee_id?.message} />
          )} />

          <Text className="mb-2 text-sm font-medium text-gray-700">Department</Text>
          <View className="mb-4">
            <ChipPicker
              options={(departments?.results ?? []).map((d) => ({ value: d.id, label: d.code }))}
              value={departmentId}
              onChange={setDepartmentId}
            />
          </View>

          <Controller control={control} name="designation" render={({ field }) => (
            <Input label="Designation" value={field.value} onChangeText={field.onChange} error={errors.designation?.message} />
          )} />
          <Controller control={control} name="qualification" render={({ field }) => (
            <Input label="Qualification" value={field.value} onChangeText={field.onChange} error={errors.qualification?.message} />
          )} />
          <Controller control={control} name="joining_date" render={({ field }) => (
            <Input label="Joining Date" placeholder="2026-08-15" value={field.value} onChangeText={field.onChange} error={errors.joining_date?.message} />
          )} />
          <Controller control={control} name="per_lecture_rate" render={({ field }) => (
            <Input label="Per Lecture Rate" keyboardType="numeric" value={field.value} onChangeText={field.onChange} error={errors.per_lecture_rate?.message} />
          )} />

          {formError && <Text className="mb-3 text-sm text-red-600">{formError}</Text>}
          <Button label="Add Teacher" onPress={handleSubmit(onSubmit)} loading={createTeacher.isPending} fullWidth />
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
