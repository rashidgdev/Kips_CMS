import * as SecureStore from 'expo-secure-store';

const ACCESS_KEY = 'kips_access_token';
const REFRESH_KEY = 'kips_refresh_token';

export const tokenStorage = {
  async getTokens(): Promise<{ access: string | null; refresh: string | null }> {
    const [access, refresh] = await Promise.all([
      SecureStore.getItemAsync(ACCESS_KEY),
      SecureStore.getItemAsync(REFRESH_KEY),
    ]);
    return { access, refresh };
  },

  async setTokens(access: string, refresh: string): Promise<void> {
    await Promise.all([SecureStore.setItemAsync(ACCESS_KEY, access), SecureStore.setItemAsync(REFRESH_KEY, refresh)]);
  },

  async setAccessToken(access: string): Promise<void> {
    await SecureStore.setItemAsync(ACCESS_KEY, access);
  },

  async clear(): Promise<void> {
    await Promise.all([SecureStore.deleteItemAsync(ACCESS_KEY), SecureStore.deleteItemAsync(REFRESH_KEY)]);
  },
};
