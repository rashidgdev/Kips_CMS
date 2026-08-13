import { forwardRef } from 'react';
import { Text, TextInput, View, type TextInputProps } from 'react-native';

type Props = TextInputProps & {
  label?: string;
  error?: string;
  required?: boolean;
};

export const Input = forwardRef<TextInput, Props>(function Input(
  { label, error, required, className = '', ...rest },
  ref,
) {
  return (
    <View className="mb-4">
      {label && (
        <Text className="mb-1.5 text-sm font-medium text-gray-700">
          {label}
          {required && <Text className="text-red-600"> *</Text>}
        </Text>
      )}
      <TextInput
        ref={ref}
        placeholderTextColor="#9ca3af"
        accessibilityLabel={label}
        className={`rounded-xl border px-3.5 py-3 text-base text-gray-900 ${
          error ? 'border-red-400 bg-red-50' : 'border-gray-300 bg-white'
        } ${className}`}
        {...rest}
      />
      {error && <Text className="mt-1 text-sm text-red-600">{error}</Text>}
    </View>
  );
});
