import { Pressable, Text, View } from 'react-native';

type Option<T> = { value: T; label: string };

export function ChipPicker<T extends string | number>({
  options,
  value,
  onChange,
}: {
  options: Option<T>[];
  value: T | null;
  onChange: (value: T) => void;
}) {
  return (
    <View className="flex-row flex-wrap gap-2">
      {options.map((option) => {
        const selected = option.value === value;
        return (
          <Pressable
            key={String(option.value)}
            accessibilityRole="button"
            accessibilityState={{ selected }}
            onPress={() => onChange(option.value)}
            className={`rounded-full border px-3.5 py-1.5 ${
              selected ? 'border-brand-700 bg-brand-700' : 'border-gray-300 bg-white'
            }`}
          >
            <Text className={`text-sm ${selected ? 'text-white' : 'text-gray-700'}`}>{option.label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}
