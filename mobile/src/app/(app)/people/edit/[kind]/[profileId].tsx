import { router, Stack, useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button, ChipPicker, ErrorState, Input, LoadingState } from '@/components/ui';
import { useSimpleCrudList } from '@/features/admin/simpleCrud';
import { usePersonProfile, useUpdatePerson } from '@/features/people/api';
import { ApiError } from '@/lib/api/client';

type Program = { id: number; name: string; code: string };
type Semester = { id: number; name: string; program: number };
type Department = { id: number; name: string; code: string };

type StudentProfileData = {
  program: number;
  current_semester: number | null;
  status: string;
};
type TeacherProfileData = {
  department: number;
  designation: string;
  per_lecture_rate: number;
  employment_status: string;
};
type StaffProfileData = { notes: string };

const STUDENT_STATUS = [
  { value: 'active', label: 'Active' },
  { value: 'graduated', label: 'Graduated' },
  { value: 'dropped', label: 'Dropped' },
  { value: 'suspended', label: 'Suspended' },
];
const EMPLOYMENT_STATUS = [
  { value: 'active', label: 'Active' },
  { value: 'on_leave', label: 'On Leave' },
  { value: 'left', label: 'Left' },
];

function StudentEditForm({ profileId }: { profileId: number }) {
  const { data, isPending, isError, error, refetch } = usePersonProfile<StudentProfileData>('students', profileId);
  const { data: programs } = useSimpleCrudList<Program>('/academics/programs/');
  const { data: semesters } = useSimpleCrudList<Semester>('/academics/semesters/');
  const update = useUpdatePerson('students', profileId);
  const [programId, setProgramId] = useState<number | null>(null);
  const [semesterId, setSemesterId] = useState<number | null>(null);
  const [status, setStatus] = useState('active');
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (data) {
      setProgramId(data.program);
      setSemesterId(data.current_semester);
      setStatus(data.status);
    }
  }, [data]);

  if (isPending) return <LoadingState />;
  if (isError) return <ErrorState error={error} onRetry={() => void refetch()} />;

  const onSubmit = () => {
    setFormError(null);
    update.mutate(
      { program: programId, current_semester: semesterId ?? '', status },
      { onSuccess: () => router.back(), onError: (err) => setFormError(err instanceof ApiError ? err.message : 'Could not save.') },
    );
  };

  const semesterOptions = semesters?.results.filter((s) => s.program === programId) ?? [];

  return (
    <View className="px-4 py-4">
      <Text className="mb-2 text-sm font-medium text-gray-700">Program</Text>
      <View className="mb-4">
        <ChipPicker
          options={(programs?.results ?? []).map((p) => ({ value: p.id, label: p.code }))}
          value={programId}
          onChange={setProgramId}
        />
      </View>
      <Text className="mb-2 text-sm font-medium text-gray-700">Current Semester</Text>
      <View className="mb-4">
        <ChipPicker
          options={semesterOptions.map((s) => ({ value: s.id, label: s.name }))}
          value={semesterId}
          onChange={setSemesterId}
        />
      </View>
      <Text className="mb-2 text-sm font-medium text-gray-700">Status</Text>
      <View className="mb-4">
        <ChipPicker options={STUDENT_STATUS} value={status} onChange={setStatus} />
      </View>
      {formError && <Text className="mb-3 text-sm text-red-600">{formError}</Text>}
      <Button label="Save" onPress={onSubmit} loading={update.isPending} fullWidth />
    </View>
  );
}

function TeacherEditForm({ profileId }: { profileId: number }) {
  const { data, isPending, isError, error, refetch } = usePersonProfile<TeacherProfileData>('teachers', profileId);
  const { data: departments } = useSimpleCrudList<Department>('/accounts/departments/');
  const update = useUpdatePerson('teachers', profileId);
  const [departmentId, setDepartmentId] = useState<number | null>(null);
  const [designation, setDesignation] = useState('');
  const [perLectureRate, setPerLectureRate] = useState('0');
  const [employmentStatus, setEmploymentStatus] = useState('active');
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (data) {
      setDepartmentId(data.department);
      setDesignation(data.designation);
      setPerLectureRate(String(data.per_lecture_rate));
      setEmploymentStatus(data.employment_status);
    }
  }, [data]);

  if (isPending) return <LoadingState />;
  if (isError) return <ErrorState error={error} onRetry={() => void refetch()} />;

  const onSubmit = () => {
    setFormError(null);
    update.mutate(
      { department: departmentId, designation, per_lecture_rate: perLectureRate, employment_status: employmentStatus },
      { onSuccess: () => router.back(), onError: (err) => setFormError(err instanceof ApiError ? err.message : 'Could not save.') },
    );
  };

  return (
    <View className="px-4 py-4">
      <Text className="mb-2 text-sm font-medium text-gray-700">Department</Text>
      <View className="mb-4">
        <ChipPicker
          options={(departments?.results ?? []).map((d) => ({ value: d.id, label: d.code }))}
          value={departmentId}
          onChange={setDepartmentId}
        />
      </View>
      <Input label="Designation" value={designation} onChangeText={setDesignation} />
      <Input label="Per Lecture Rate" keyboardType="numeric" value={perLectureRate} onChangeText={setPerLectureRate} />
      <Text className="mb-2 text-sm font-medium text-gray-700">Employment Status</Text>
      <View className="mb-4">
        <ChipPicker options={EMPLOYMENT_STATUS} value={employmentStatus} onChange={setEmploymentStatus} />
      </View>
      {formError && <Text className="mb-3 text-sm text-red-600">{formError}</Text>}
      <Button label="Save" onPress={onSubmit} loading={update.isPending} fullWidth />
    </View>
  );
}

function StaffEditForm({ profileId }: { profileId: number }) {
  const { data, isPending, isError, error, refetch } = usePersonProfile<StaffProfileData>('staff', profileId);
  const update = useUpdatePerson('staff', profileId);
  const [notes, setNotes] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (data) setNotes(data.notes);
  }, [data]);

  if (isPending) return <LoadingState />;
  if (isError) return <ErrorState error={error} onRetry={() => void refetch()} />;

  const onSubmit = () => {
    setFormError(null);
    update.mutate(
      { notes },
      { onSuccess: () => router.back(), onError: (err) => setFormError(err instanceof ApiError ? err.message : 'Could not save.') },
    );
  };

  return (
    <View className="px-4 py-4">
      <Input label="Notes" value={notes} onChangeText={setNotes} />
      {formError && <Text className="mb-3 text-sm text-red-600">{formError}</Text>}
      <Button label="Save" onPress={onSubmit} loading={update.isPending} fullWidth />
    </View>
  );
}

export default function PersonEditScreen() {
  const { kind, profileId } = useLocalSearchParams<{ kind: string; profileId: string }>();
  const id = Number(profileId);

  return (
    <SafeAreaView className="flex-1 bg-white">
      <Stack.Screen options={{ headerShown: true, title: 'Edit' }} />
      {kind === 'student' ? (
        <StudentEditForm profileId={id} />
      ) : kind === 'teacher' ? (
        <TeacherEditForm profileId={id} />
      ) : (
        <StaffEditForm profileId={id} />
      )}
    </SafeAreaView>
  );
}
