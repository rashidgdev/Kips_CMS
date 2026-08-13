import Ionicons from '@expo/vector-icons/Ionicons';
import { router, type Href } from 'expo-router';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { useAuth } from '@/lib/auth/AuthContext';

type MenuItem = { label: string; route: Href; icon: keyof typeof Ionicons.glyphMap; adminOnly?: boolean };
type Section = { title: string; items: MenuItem[] };

const SECTIONS: Section[] = [
  {
    title: 'People',
    items: [{ label: 'People Directory', route: '/people', icon: 'people' }],
  },
  {
    title: 'Academics',
    items: [
      { label: 'Departments', route: '/admin/departments', icon: 'business' },
      { label: 'Programs', route: '/admin/programs', icon: 'school' },
      { label: 'Semesters', route: '/admin/semesters', icon: 'calendar' },
      { label: 'Courses', route: '/admin/courses', icon: 'book' },
      { label: 'Course Offerings', route: '/admin/offerings', icon: 'layers' },
      { label: 'Enroll by Offering', route: '/admin/enroll-by-offering', icon: 'person-add' },
      { label: 'Enroll by Student', route: '/admin/enroll-by-student', icon: 'person-add' },
    ],
  },
  {
    title: 'Timetable Setup',
    items: [
      { label: 'Rooms', route: '/admin/rooms', icon: 'business' },
      { label: 'Time Slots', route: '/admin/timeslots', icon: 'time' },
    ],
  },
  {
    title: 'Assessments & Fees Setup',
    items: [
      { label: 'Assessment Categories', route: '/admin/assessment-categories', icon: 'document-text' },
      { label: 'Fee Categories', route: '/admin/fee-categories', icon: 'pricetag' },
      { label: 'Fee Structures', route: '/admin/fee-structures', icon: 'cash' },
    ],
  },
];

export default function AdministrationScreen() {
  const { user } = useAuth();

  return (
    <SafeAreaView className="flex-1 bg-gray-50" edges={['bottom']}>
      <ScrollView contentContainerClassName="px-4 py-4 gap-5">
        {SECTIONS.map((section) => (
          <View key={section.title}>
            <Text className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">{section.title}</Text>
            <View className="overflow-hidden rounded-2xl border border-gray-200 bg-white">
              {section.items.map((item, index) => (
                <Pressable
                  key={item.route as string}
                  accessibilityRole="button"
                  onPress={() => router.push(item.route)}
                  className={`flex-row items-center px-4 py-3.5 active:bg-gray-50 ${
                    index > 0 ? 'border-t border-gray-100' : ''
                  }`}
                >
                  <Ionicons name={item.icon} size={20} color="#4b5563" />
                  <Text className="ml-3 flex-1 text-base text-gray-800">{item.label}</Text>
                  <Ionicons name="chevron-forward" size={18} color="#9ca3af" />
                </Pressable>
              ))}
            </View>
          </View>
        ))}

        {user?.role === 'admin' && (
          <Text className="px-1 text-xs text-gray-400">
            Staff account management (add Coordinator/Accountant/Admin) is available from the People directory.
          </Text>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
