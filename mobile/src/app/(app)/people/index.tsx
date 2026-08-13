import Ionicons from '@expo/vector-icons/Ionicons';
import { router, Stack } from 'expo-router';
import { useState } from 'react';
import { FlatList, Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Badge, Card, EmptyState, ErrorState, Input, LoadingState } from '@/components/ui';
import { usePeople, useToggleActive } from '@/features/people/api';

const ROLE_FILTERS = [
  { value: '', label: 'All' },
  { value: 'student', label: 'Students' },
  { value: 'teacher', label: 'Teachers' },
  { value: 'hod', label: 'HODs' },
  { value: 'coordinator', label: 'Coordinators' },
  { value: 'accountant', label: 'Accountants' },
  { value: 'admin', label: 'Admins' },
];

export default function PeopleDirectoryScreen() {
  const [role, setRole] = useState('');
  const [query, setQuery] = useState('');
  const { data, isPending, isError, error, refetch } = usePeople({ role, q: query });
  const toggleActive = useToggleActive();

  return (
    <SafeAreaView className="flex-1 bg-gray-50">
      <Stack.Screen options={{ headerShown: true, title: 'People' }} />

      <View className="px-4 pt-4">
        <Input placeholder="Search by name or username" value={query} onChangeText={setQuery} />
      </View>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} className="mb-2 max-h-11 grow-0">
        <View className="flex-row gap-2 px-4">
          {ROLE_FILTERS.map((r) => {
            const selected = r.value === role;
            return (
              <Pressable
                key={r.value}
                accessibilityRole="button"
                onPress={() => setRole(r.value)}
                className={`rounded-full border px-3.5 py-1.5 ${
                  selected ? 'border-brand-700 bg-brand-700' : 'border-gray-300 bg-white'
                }`}
              >
                <Text className={`text-xs font-medium ${selected ? 'text-white' : 'text-gray-700'}`}>{r.label}</Text>
              </Pressable>
            );
          })}
        </View>
      </ScrollView>

      <ScrollView horizontal showsHorizontalScrollIndicator={false} className="mb-2 max-h-11 grow-0">
        <View className="flex-row gap-2 px-4">
          {[
            { label: 'Add Student', route: '/people/student-new' as const },
            { label: 'Add Teacher', route: '/people/teacher-new' as const },
            { label: 'Add Staff', route: '/people/staff-new' as const },
          ].map((action) => (
            <Pressable
              key={action.route}
              accessibilityRole="button"
              onPress={() => router.push(action.route)}
              className="flex-row items-center gap-1 rounded-full border border-brand-700 bg-white px-3.5 py-1.5"
            >
              <Ionicons name="add" size={14} color="#1d4ed8" />
              <Text className="text-xs font-semibold text-brand-700">{action.label}</Text>
            </Pressable>
          ))}
        </View>
      </ScrollView>

      {isPending ? (
        <LoadingState />
      ) : isError ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : (
        <FlatList
          data={data}
          keyExtractor={(item) => String(item.id)}
          contentContainerClassName="px-4 py-2 gap-2"
          ListEmptyComponent={<EmptyState title="No people match your search" />}
          renderItem={({ item }) => (
            <Card
              onPress={
                item.profile_id
                  ? () => {
                      const kind =
                        item.role === 'student' ? 'student' : item.role === 'teacher' || item.role === 'hod' ? 'teacher' : 'staff';
                      router.push({
                        pathname: '/people/edit/[kind]/[profileId]',
                        params: { kind, profileId: String(item.profile_id) },
                      });
                    }
                  : undefined
              }
            >
              <View className="flex-row items-center justify-between">
                <View className="flex-1">
                  <Text className="text-sm font-semibold text-gray-900">{item.full_name}</Text>
                  <Text className="mt-0.5 text-xs text-gray-500">
                    @{item.username} {item.identifier ? `· ${item.identifier}` : ''}
                  </Text>
                  {item.department && <Text className="mt-0.5 text-xs text-gray-400">{item.department}</Text>}
                </View>
                <View className="items-end gap-1.5">
                  <Badge label={item.role_display} tone="brand" />
                  <Pressable
                    accessibilityRole="button"
                    onPress={() => toggleActive.mutate(item.id)}
                    className="px-1 py-0.5"
                  >
                    <Text className={`text-xs font-medium ${item.is_active ? 'text-green-700' : 'text-gray-400'}`}>
                      {item.is_active ? 'Active' : 'Inactive'}
                    </Text>
                  </Pressable>
                </View>
              </View>
            </Card>
          )}
        />
      )}
    </SafeAreaView>
  );
}
