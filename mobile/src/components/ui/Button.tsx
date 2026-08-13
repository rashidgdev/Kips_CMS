import { ActivityIndicator, Pressable, Text } from 'react-native';

import { Colors } from '@/constants/theme';

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost';

type Props = {
  label: string;
  onPress: () => void;
  variant?: Variant;
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
};

const VARIANT_CLASSES: Record<Variant, string> = {
  primary: 'bg-brand-700 active:bg-brand-800',
  secondary: 'bg-white border border-gray-300 active:bg-gray-50',
  danger: 'bg-red-600 active:bg-red-700',
  ghost: 'bg-transparent active:bg-gray-100',
};

const VARIANT_TEXT_CLASSES: Record<Variant, string> = {
  primary: 'text-white',
  secondary: 'text-gray-800',
  danger: 'text-white',
  ghost: 'text-brand-700',
};

export function Button({ label, onPress, variant = 'primary', loading, disabled, fullWidth }: Props) {
  const isDisabled = disabled || loading;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled: isDisabled, busy: loading }}
      onPress={onPress}
      disabled={isDisabled}
      className={`flex-row items-center justify-center rounded-xl px-4 py-3 ${VARIANT_CLASSES[variant]} ${
        isDisabled ? 'opacity-50' : ''
      } ${fullWidth ? 'w-full' : ''}`}
    >
      {loading && (
        <ActivityIndicator
          size="small"
          color={variant === 'primary' || variant === 'danger' ? '#ffffff' : Colors.brand}
          className="mr-2"
        />
      )}
      <Text className={`text-center text-base font-semibold ${VARIANT_TEXT_CLASSES[variant]}`}>{label}</Text>
    </Pressable>
  );
}
