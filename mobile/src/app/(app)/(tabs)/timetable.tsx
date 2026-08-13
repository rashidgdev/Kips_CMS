import Ionicons from '@expo/vector-icons/Ionicons';
import { router } from 'expo-router';
import { useState } from 'react';
import { Alert, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Button, ErrorState, LoadingState } from '@/components/ui';
import { DayGrid } from '@/features/timetable/DayGrid';
import {
  useSemesterGrid,
  useSemesters,
  useStudentGrid,
  useTeacherGrid,
  useUnscheduleEntry,
} from '@/features/timetable/api';
import { useAuth } from '@/lib/auth/AuthContext';
import { useDownloadPdf } from '@/lib/pdf';

function DownloadPdfButton({ pdfUrl, filename }: { pdfUrl: string | null; filename: string }) {
  const download = useDownloadPdf();
  if (!pdfUrl) return null;
  return (
    <View className="px-4 pb-3">
      <Button
        label="Download PDF"
        variant="secondary"
        loading={download.isPending}
        onPress={() => download.mutate({ path: pdfUrl, filename })}
      />
      {download.isError && (
        <Text className="mt-2 text-center text-xs text-red-600">{download.error.message}</Text>
      )}
    </View>
  );
}

function StaffTimetable() {
  const { data: semesters, isPending: semestersPending } = useSemesters();
  const [semesterId, setSemesterId] = useState<number | null>(null);
  const activeSemesterId = semesterId ?? semesters?.find((s) => s.is_current)?.id ?? semesters?.[0]?.id ?? null;
  const { data, isPending, isError, error, refetch } = useSemesterGrid(activeSemesterId);
  const unschedule = useUnscheduleEntry(activeSemesterId ?? 0);

  const onCellPress = (entryId: number) => {
    Alert.alert('Remove class', 'Remove this class from the timetable?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Remove',
        style: 'destructive',
        onPress: () => unschedule.mutate(entryId, { onError: () => Alert.alert('Could not remove this class.') }),
      },
    ]);
  };

  if (semestersPending || isPending) return <LoadingState />;
  if (isError) return <ErrorState error={error} onRetry={() => void refetch()} />;

  return (
    <View className="flex-1">
      {semesters && semesters.length > 1 && (
        <ScrollView horizontal showsHorizontalScrollIndicator={false} className="mb-2 max-h-12 grow-0">
          <View className="flex-row gap-2 px-4">
            {semesters.map((sem) => {
              const selected = sem.id === activeSemesterId;
              return (
                <Pressable
                  key={sem.id}
                  accessibilityRole="button"
                  onPress={() => setSemesterId(sem.id)}
                  className={`rounded-full border px-3.5 py-1.5 ${
                    selected ? 'border-brand-700 bg-brand-700' : 'border-gray-300 bg-white'
                  }`}
                >
                  <Text className={`text-xs font-medium ${selected ? 'text-white' : 'text-gray-700'}`}>
                    {sem.name}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        </ScrollView>
      )}
      <View className="flex-row items-center justify-between px-4 pb-2">
        <Text className="text-xs text-gray-500">Tap a class to remove it</Text>
        <Pressable
          accessibilityRole="button"
          onPress={() =>
            activeSemesterId &&
            router.push({ pathname: '/timetable/schedule/[semesterId]', params: { semesterId: String(activeSemesterId) } })
          }
          className="flex-row items-center gap-1"
        >
          <Ionicons name="add-circle" size={16} color="#1d4ed8" />
          <Text className="text-xs font-semibold text-brand-700">Schedule Class</Text>
        </Pressable>
      </View>
      <DayGrid grid={data.grid} onCellPress={onCellPress} />
      <DownloadPdfButton pdfUrl={data.pdf_url} filename={`timetable-${data.semester?.name ?? 'semester'}.pdf`} />
    </View>
  );
}

function TeacherTimetable() {
  const { data, isPending, isError, error, refetch } = useTeacherGrid();
  if (isPending) return <LoadingState />;
  if (isError) return <ErrorState error={error} onRetry={() => void refetch()} />;
  return (
    <View className="flex-1">
      <DayGrid grid={data.grid} />
      <DownloadPdfButton pdfUrl={data.pdf_url} filename="my-timetable.pdf" />
    </View>
  );
}

function StudentTimetable() {
  const { data, isPending, isError, error, refetch } = useStudentGrid();
  if (isPending) return <LoadingState />;
  if (isError) return <ErrorState error={error} onRetry={() => void refetch()} />;
  return (
    <View className="flex-1">
      <DayGrid grid={data.grid} />
      <DownloadPdfButton pdfUrl={data.pdf_url} filename="my-timetable.pdf" />
    </View>
  );
}

export default function TimetableScreen() {
  const { user } = useAuth();

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      {user?.role === 'coordinator' || user?.role === 'admin' ? (
        <StaffTimetable />
      ) : user?.role === 'teacher' || user?.role === 'hod' ? (
        <TeacherTimetable />
      ) : (
        <StudentTimetable />
      )}
    </SafeAreaView>
  );
}
