import { useMutation } from '@tanstack/react-query';
import { Directory, File, Paths } from 'expo-file-system';
import * as Sharing from 'expo-sharing';

import { API_BASE_URL } from '@/lib/api/config';
import { useAuth } from '@/lib/auth/AuthContext';

// Strips the /api/v1 suffix - PDF/export endpoints are plain Django views
// mounted at the server root, not under the REST API prefix. Authenticated
// via the JWTBridgeMiddleware (apps/common/middleware.py), which is why the
// same Bearer token that authenticates JSON API calls also works here.
const SERVER_ORIGIN = API_BASE_URL.replace(/\/api\/v1\/?$/, '');

/**
 * Downloads a PDF (or any file) from a server-relative path with the
 * current access token attached, then opens the native share/open sheet -
 * the standard Expo-Go-compatible pattern for authenticated downloads
 * (there's no way to just point a native PDF viewer at an authenticated
 * URL directly).
 */
export async function downloadAndShare(relativePath: string, accessToken: string | null, filename: string) {
  if (!accessToken) throw new Error('Not signed in.');

  const url = relativePath.startsWith('http') ? relativePath : SERVER_ORIGIN + relativePath;
  const destination = new Directory(Paths.cache, 'kips-downloads');
  if (!destination.exists) destination.create({ intermediates: true });

  const downloaded = await File.downloadFileAsync(url, destination, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });

  const renamed = new File(destination, filename);
  if (renamed.exists) renamed.delete();
  downloaded.move(renamed);

  const canShare = await Sharing.isAvailableAsync();
  if (canShare) {
    await Sharing.shareAsync(renamed.uri, { mimeType: 'application/pdf' });
  }
  return renamed.uri;
}

/** Wraps downloadAndShare with the current user's access token and a loading/error state. */
export function useDownloadPdf() {
  const { getAccessToken } = useAuth();
  return useMutation({
    mutationFn: ({ path, filename }: { path: string; filename: string }) =>
      downloadAndShare(path, getAccessToken(), filename),
  });
}
