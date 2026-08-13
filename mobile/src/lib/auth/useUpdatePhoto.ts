import { useMutation, useQueryClient } from '@tanstack/react-query';
import * as ImagePicker from 'expo-image-picker';

import { apiFetch } from '@/lib/api/client';

import { useAuth } from './AuthContext';

/** Picks a photo from the library and PATCHes it to /accounts/me/photo/, then refreshes the cached user. */
export function useUpdatePhoto() {
  const { refreshMe } = useAuth();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async () => {
      const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (!permission.granted) {
        throw new Error('Photo library permission is required to change your profile picture.');
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [1, 1],
        quality: 0.7,
      });
      if (result.canceled || !result.assets[0]) return null;

      const asset = result.assets[0];
      const form = new FormData();
      form.append('photo', {
        uri: asset.uri,
        name: asset.fileName ?? 'photo.jpg',
        type: asset.mimeType ?? 'image/jpeg',
      } as unknown as Blob);

      return apiFetch.patchForm<{ photo_url: string | null }>('/accounts/me/photo/', form);
    },
    onSuccess: async (result) => {
      if (result === null) return; // user cancelled
      await refreshMe();
      await queryClient.invalidateQueries();
    },
  });
}
