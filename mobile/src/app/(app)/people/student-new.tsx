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

type Program = { id: number; name: string; code: string };
type Semester = { id: number; name: string; program: number };

type StudentInput = {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  roll_number: string;
  admission_date: string;
  date_of_birth: string;
  address: string;
  guardian_name: string;
  guardian_phone: string;
  cnic: string;
};

const FIELDS = [
  'username', 'first_name', 'last_name', 'email', 'phone_number', 'photo', 'roll_number',
  'program', 'current_semester', 'admission_date', 'date_of_birth', 'gender', 'address',
  'guardian_name', 'guardian_phone', 'cnic',
];

export default function StudentCreateScreen() {
  const router = useRouter();
  const { data: programs } = useSimpleCrudList<Program>('/academics/programs/');
  const { data: semesters } = useSimpleCrudList<Semester>('/academics/semesters/');
  const createStudent = useCreatePerson('students');

  const [programId, setProgramId] = useState<number | null>(null);
  const [semesterId, setSemesterId] = useState<number | null>(null);
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [result, setResult] = useState<CreatePersonResult | null>(null);

  const {
    control,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<StudentInput>({
    defaultValues: {
      username: '', first_name: '', last_name: '', email: '', phone_number: '',
      roll_number: '', admission_date: '', date_of_birth: '', address: '',
      guardian_name: '', guardian_phone: '', cnic: '',
    },
  });

  if (result) {
    return (
      <SafeAreaView className="flex-1 bg-gray-50">
        <Stack.Screen options={{ headerShown: true, title: 'Student Added' }} />
        <View className="px-4 py-4">
          <TempPasswordCard username={result.username} tempPassword={result.temp_password} onDone={() => router.back()} />
        </View>
      </SafeAreaView>
    );
  }

  const onSubmit = async (data: StudentInput) => {
    setFormError(null);
    if (!programId) {
      setFormError('Select a program.');
      return;
    }
    try {
      const res = await createStudent.mutateAsync({
        fields: { ...data, program: programId, current_semester: semesterId ?? '' },
        photoUri,
      });
      setResult(res);
    } catch (error) {
      setFormError(applyServerErrors(error, setError, FIELDS));
    }
  };

  const semesterOptions = semesters?.results.filter((s) => s.program === programId) ?? [];

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ headerShown: true, title: 'Add Student' }} />
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

          <Controller control={control} name="roll_number" render={({ field }) => (
            <Input label="Roll Number" value={field.value} onChangeText={field.onChange} error={errors.roll_number?.message} />
          )} />

          <Text className="mb-2 text-sm font-medium text-gray-700">Program</Text>
          <View className="mb-4">
            <ChipPicker
              options={(programs?.results ?? []).map((p) => ({ value: p.id, label: p.code }))}
              value={programId}
              onChange={(v) => {
                setProgramId(v);
                setSemesterId(null);
              }}
            />
          </View>

          {semesterOptions.length > 0 && (
            <>
              <Text className="mb-2 text-sm font-medium text-gray-700">Current Semester (optional)</Text>
              <View className="mb-4">
                <ChipPicker
                  options={semesterOptions.map((s) => ({ value: s.id, label: s.name }))}
                  value={semesterId}
                  onChange={setSemesterId}
                />
              </View>
            </>
          )}

          <Controller control={control} name="admission_date" render={({ field }) => (
            <Input label="Admission Date" placeholder="2026-08-15" value={field.value} onChangeText={field.onChange} error={errors.admission_date?.message} />
          )} />
          <Controller control={control} name="date_of_birth" render={({ field }) => (
            <Input label="Date of Birth (optional)" placeholder="2005-01-01" value={field.value} onChangeText={field.onChange} error={errors.date_of_birth?.message} />
          )} />
          <Controller control={control} name="guardian_name" render={({ field }) => (
            <Input label="Guardian Name" value={field.value} onChangeText={field.onChange} error={errors.guardian_name?.message} />
          )} />
          <Controller control={control} name="guardian_phone" render={({ field }) => (
            <Input label="Guardian Phone" value={field.value} onChangeText={field.onChange} error={errors.guardian_phone?.message} />
          )} />
          <Controller control={control} name="cnic" render={({ field }) => (
            <Input label="CNIC" value={field.value} onChangeText={field.onChange} error={errors.cnic?.message} />
          )} />
          <Controller control={control} name="address" render={({ field }) => (
            <Input label="Address" value={field.value} onChangeText={field.onChange} error={errors.address?.message} />
          )} />

          {formError && <Text className="mb-3 text-sm text-red-600">{formError}</Text>}
          <Button label="Add Student" onPress={handleSubmit(onSubmit)} loading={createStudent.isPending} fullWidth />
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
