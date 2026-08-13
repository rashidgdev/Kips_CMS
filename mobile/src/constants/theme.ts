/**
 * Raw color values for native components that can't take a Tailwind
 * className (ActivityIndicator, StatusBar, icon tint props, etc). Screen
 * styling itself uses NativeWind classes - see tailwind.config.js for the
 * `brand` palette shared with these.
 */
export const Colors = {
  brand: '#1d4ed8', // brand-700
  brandDark: '#1e3a8a', // brand-900
  danger: '#dc2626',
  warning: '#d97706',
  success: '#16a34a',
  textMuted: '#6b7280',
  border: '#e5e7eb',
} as const;
