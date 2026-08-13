const RAW_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL;

if (!RAW_BASE_URL) {
  throw new Error(
    'EXPO_PUBLIC_API_BASE_URL is not set. Copy mobile/.env.example to mobile/.env and fill in ' +
      "your Django server's LAN address (see the comments in that file for how to find it).",
  );
}

// Strip any trailing slash so callers can always write `apiFetch('/foo/')`
// without worrying about a double slash.
export const API_BASE_URL = RAW_BASE_URL.replace(/\/+$/, '');
