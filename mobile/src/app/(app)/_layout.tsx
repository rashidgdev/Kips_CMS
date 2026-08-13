import { Redirect, Stack } from 'expo-router';

import { LoadingState } from '@/components/ui';
import { useAuth } from '@/lib/auth/AuthContext';

/**
 * Guards every screen under (app) - covers direct/deep links into an app
 * route, not just navigation from within the app. Phase 3 replaces the
 * plain Stack below with role-based tab navigation; the guard logic here
 * stays the same.
 */
export default function AppLayout() {
  const { isBootstrapping, isAuthenticated, user } = useAuth();

  if (isBootstrapping) return <LoadingState label="Loading KIPS CMS…" />;
  if (!isAuthenticated) return <Redirect href="/(auth)/login" />;
  if (user?.must_change_password) return <Redirect href="/(auth)/change-password" />;

  return <Stack screenOptions={{ headerShown: false }} />;
}
