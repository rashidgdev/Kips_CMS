import type Ionicons from '@expo/vector-icons/Ionicons';
import type { Role } from '@/lib/auth/types';

type IconName = keyof typeof Ionicons.glyphMap;

export type NavItem = {
  key: string;
  label: string;
  /** Route within (app)/(tabs)/. */
  route: string;
  icon: IconName;
};

/**
 * Mirrors apps/common/context_processors.py::NAV_CONFIG exactly - one entry
 * per web nav link, same labels, same set of destinations per role. This is
 * NOT the permission system (the server still enforces every screen's real
 * access via HasRole/ownership checks - a 403 is handled generically), it
 * only decides what's *shown*, exactly like NAV_CONFIG does for the web
 * template's sidebar.
 *
 * Split into `primary` (bottom tab bar, capped at 4 so the tab bar doesn't
 * get cramped) and `more` (reachable via the always-present "More" tab) -
 * an explicit mobile-UX adaptation of the web's flat link list. "Admin
 * Panel" (raw Django admin site, admin role only) is intentionally dropped:
 * it's an HTML-only interface with no REST API backing, not part of the
 * mobile app's scope - see the mobile app's plan doc.
 */
export const NAV_CONFIG: Record<Role, { primary: NavItem[]; more: NavItem[] }> = {
  student: {
    primary: [
      { key: 'dashboard', label: 'Dashboard', route: '/', icon: 'home' },
      { key: 'attendance', label: 'Attendance', route: '/attendance', icon: 'checkmark-done' },
      { key: 'grades', label: 'Grades', route: '/grades', icon: 'school' },
      { key: 'timetable', label: 'Timetable', route: '/timetable', icon: 'calendar' },
    ],
    more: [{ key: 'fees', label: 'Fees', route: '/fees', icon: 'cash' }],
  },
  teacher: {
    primary: [
      { key: 'dashboard', label: 'Dashboard', route: '/', icon: 'home' },
      { key: 'attendance', label: 'Attendance', route: '/attendance', icon: 'checkmark-done' },
      { key: 'daybook', label: 'Day Book', route: '/daybook', icon: 'book' },
      { key: 'assessments', label: 'Assessments', route: '/assessments', icon: 'document-text' },
    ],
    more: [
      { key: 'timetable', label: 'Timetable', route: '/timetable', icon: 'calendar' },
      { key: 'reports', label: 'Reports', route: '/reports', icon: 'bar-chart' },
    ],
  },
  hod: {
    primary: [
      { key: 'dashboard', label: 'Dashboard', route: '/', icon: 'home' },
      { key: 'attendance', label: 'Attendance', route: '/attendance', icon: 'checkmark-done' },
      { key: 'daybook', label: 'Day Book', route: '/daybook', icon: 'book' },
      { key: 'assessments', label: 'Assessments', route: '/assessments', icon: 'document-text' },
    ],
    more: [
      { key: 'timetable', label: 'Timetable', route: '/timetable', icon: 'calendar' },
      { key: 'reports', label: 'Reports', route: '/reports', icon: 'bar-chart' },
    ],
  },
  coordinator: {
    primary: [
      { key: 'dashboard', label: 'Dashboard', route: '/', icon: 'home' },
      { key: 'administration', label: 'Administration', route: '/administration', icon: 'settings' },
      { key: 'timetable', label: 'Timetable', route: '/timetable', icon: 'calendar' },
      { key: 'student-fees', label: 'Student Fees', route: '/student-fees', icon: 'cash' },
    ],
    more: [
      { key: 'verify-daybook', label: 'Verify Day Book', route: '/verify-daybook', icon: 'checkmark-circle' },
      { key: 'reports', label: 'Reports', route: '/reports', icon: 'bar-chart' },
    ],
  },
  accountant: {
    primary: [
      { key: 'dashboard', label: 'Dashboard', route: '/', icon: 'home' },
      { key: 'student-fees', label: 'Student Fees', route: '/student-fees', icon: 'cash' },
      { key: 'challans', label: 'Challans', route: '/challans', icon: 'document-text' },
      { key: 'administration', label: 'Administration', route: '/administration', icon: 'settings' },
    ],
    more: [],
  },
  admin: {
    primary: [
      { key: 'dashboard', label: 'Dashboard', route: '/', icon: 'home' },
      { key: 'administration', label: 'Administration', route: '/administration', icon: 'settings' },
      { key: 'timetable', label: 'Timetable', route: '/timetable', icon: 'calendar' },
      { key: 'student-fees', label: 'Student Fees', route: '/student-fees', icon: 'cash' },
    ],
    more: [
      { key: 'verify-daybook', label: 'Verify Day Book', route: '/verify-daybook', icon: 'checkmark-circle' },
      { key: 'challans', label: 'Challans', route: '/challans', icon: 'document-text' },
      { key: 'reports', label: 'Reports', route: '/reports', icon: 'bar-chart' },
    ],
  },
};

/** Every route key that exists as a (tabs) screen file, across every role - drives which Tabs.Screen entries get href=null. */
export function isPrimaryForRole(role: Role, key: string): boolean {
  return NAV_CONFIG[role].primary.some((item) => item.key === key);
}
