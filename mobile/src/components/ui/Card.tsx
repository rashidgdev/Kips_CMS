import { Pressable, View, type PressableProps, type ViewProps } from 'react-native';

type Props = ViewProps & {
  className?: string;
  /** When provided, the card renders as a proper touch target (Pressable) instead of a static View. */
  onPress?: PressableProps['onPress'];
};

export function Card({ className = '', onPress, ...rest }: Props) {
  const classes = `rounded-2xl border border-gray-200 bg-white p-4 shadow-sm ${className}`;

  if (onPress) {
    return (
      <Pressable
        accessibilityRole="button"
        onPress={onPress}
        className={`${classes} active:bg-gray-50`}
        {...(rest as PressableProps)}
      />
    );
  }

  return <View className={classes} {...rest} />;
}
