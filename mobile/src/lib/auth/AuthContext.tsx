import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';

import { ApiError, apiFetch, registerAuthHooks } from '@/lib/api/client';

import { tokenStorage } from './tokenStorage';
import type { Me, TokenPair } from './types';

type AuthContextValue = {
  /** True only while restoring a session on app start - not during login/logout actions. */
  isBootstrapping: boolean;
  isAuthenticated: boolean;
  user: Me | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  /** Re-fetches /me/ - call after change-password clears must_change_password server-side. */
  refreshMe: () => Promise<void>;
  /** For the rare case (PDF downloads via expo-file-system) that needs the raw token outside apiFetch. */
  getAccessToken: () => string | null;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isBootstrapping, setIsBootstrapping] = useState(true);
  const [user, setUser] = useState<Me | null>(null);

  // Mirrors state in a ref so the module-level apiClient hooks (which are
  // plain functions, not React state) always read the current token/user
  // without needing to re-register on every render.
  const accessTokenRef = useRef<string | null>(null);
  const refreshTokenRef = useRef<string | null>(null);
  const refreshInFlightRef = useRef<Promise<string | null> | null>(null);

  const fetchMe = useCallback(async (): Promise<void> => {
    const me = await apiFetch.get<Me>('/accounts/me/');
    setUser(me);
  }, []);

  const clearSession = useCallback(async () => {
    accessTokenRef.current = null;
    refreshTokenRef.current = null;
    setUser(null);
    await tokenStorage.clear();
  }, []);

  const applyTokens = useCallback(async (tokens: TokenPair) => {
    accessTokenRef.current = tokens.access;
    refreshTokenRef.current = tokens.refresh;
    await tokenStorage.setTokens(tokens.access, tokens.refresh);
  }, []);

  const doRefresh = useCallback(async (): Promise<string | null> => {
    if (refreshInFlightRef.current) return refreshInFlightRef.current;

    const run = async () => {
      const refreshToken = refreshTokenRef.current;
      if (!refreshToken) return null;
      try {
        const { access } = await apiFetch.post<{ access: string }>(
          '/accounts/token/refresh/',
          { refresh: refreshToken },
          { auth: false },
        );
        accessTokenRef.current = access;
        await tokenStorage.setAccessToken(access);
        return access;
      } catch {
        return null;
      }
    };

    const promise = run();
    refreshInFlightRef.current = promise;
    try {
      return await promise;
    } finally {
      refreshInFlightRef.current = null;
    }
  }, []);

  useEffect(() => {
    registerAuthHooks({
      getAccessToken: () => accessTokenRef.current,
      refreshAccessToken: doRefresh,
      onAuthenticationFailed: () => {
        void clearSession();
      },
    });
  }, [doRefresh, clearSession]);

  // Restore a previous session on app start.
  useEffect(() => {
    (async () => {
      const { access, refresh } = await tokenStorage.getTokens();
      if (!access || !refresh) {
        setIsBootstrapping(false);
        return;
      }
      accessTokenRef.current = access;
      refreshTokenRef.current = refresh;
      try {
        await fetchMe();
      } catch (error) {
        // Access token expired and refresh also failed (or the account was
        // deactivated server-side) - apiClient's 401 handler already tried
        // a refresh before this rejects, so there's nothing left to do but
        // drop back to the login screen.
        if (error instanceof ApiError) {
          await clearSession();
        }
      } finally {
        setIsBootstrapping(false);
      }
    })();
  }, [fetchMe, clearSession]);

  const login = useCallback(
    async (username: string, password: string) => {
      const tokens = await apiFetch.post<TokenPair>('/accounts/token/', { username, password }, { auth: false });
      await applyTokens(tokens);
      await fetchMe();
    },
    [applyTokens, fetchMe],
  );

  const logout = useCallback(async () => {
    await clearSession();
  }, [clearSession]);

  const getAccessToken = useCallback(() => accessTokenRef.current, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      isBootstrapping,
      isAuthenticated: user !== null,
      user,
      login,
      logout,
      refreshMe: fetchMe,
      getAccessToken,
    }),
    [isBootstrapping, user, login, logout, fetchMe, getAccessToken],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
