import Ionicons from '@expo/vector-icons/Ionicons';
import { Tabs } from 'expo-router';

import { Colors } from '@/constants/theme';
import { NAV_CONFIG } from '@/constants/navConfig';
import { useAuth } from '@/lib/auth/AuthContext';

/**
 * One physical tab bar shared by every role - which screens actually show
 * as tabs is computed from NAV_CONFIG per the logged-in user's role (Expo
 * Router's recommended pattern: every possible screen is registered, unused
 * ones get `href: null` to hide them without unmounting the route). "More"
 * is always present as the last tab regardless of role, so there's always a
 * reachable profile/logout screen even for roles with an empty `more` list.
 */
export default function TabsLayout() {
  const { user } = useAuth();
  const role = user!.role; // (app)/_layout.tsx already guarantees an authenticated, non-forced user here.
  const primaryKeys = new Set(NAV_CONFIG[role].primary.map((item) => item.key));

  const screen = (key: string, label: string, icon: keyof typeof Ionicons.glyphMap) => (
    <Tabs.Screen
      key={key}
      name={key === 'dashboard' ? 'index' : key}
      options={{
        title: label,
        href: primaryKeys.has(key) ? undefined : null,
        tabBarIcon: ({ color, size }) => <Ionicons name={icon} size={size} color={color} />,
      }}
    />
  );

  return (
    <Tabs
      screenOptions={{
        headerTitleAlign: 'left',
        tabBarActiveTintColor: Colors.brand,
        tabBarInactiveTintColor: '#9ca3af',
      }}
    >
      {screen('dashboard', 'Dashboard', 'home')}
      {screen('attendance', 'Attendance', 'checkmark-done')}
      {screen('grades', 'Grades', 'school')}
      {screen('daybook', 'Day Book', 'book')}
      {screen('assessments', 'Assessments', 'document-text')}
      {screen('timetable', 'Timetable', 'calendar')}
      {screen('fees', 'Fees', 'cash')}
      {screen('administration', 'Administration', 'settings')}
      {screen('student-fees', 'Student Fees', 'cash')}
      {screen('verify-daybook', 'Verify Day Book', 'checkmark-circle')}
      {screen('challans', 'Challans', 'document-text')}
      {screen('reports', 'Reports', 'bar-chart')}
      <Tabs.Screen
        name="more"
        options={{
          title: 'More',
          tabBarIcon: ({ color, size }) => <Ionicons name="menu" size={size} color={color} />,
        }}
      />
    </Tabs>
  );
}
