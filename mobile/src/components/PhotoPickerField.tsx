import Ionicons from '@expo/vector-icons/Ionicons';
import { Image } from 'expo-image';
import * as ImagePicker from 'expo-image-picker';
import { Pressable, Text, View } from 'react-native';

export function PhotoPickerField({
  uri,
  onChange,
}: {
  uri: string | null;
  onChange: (uri: string | null) => void;
}) {
  const pick = async () => {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) return;
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.7,
    });
    if (!result.canceled && result.assets[0]) onChange(result.assets[0].uri);
  };

  return (
    <View className="mb-4">
      <Text className="mb-1.5 text-sm font-medium text-gray-700">Photo (optional)</Text>
      <Pressable
        accessibilityRole="button"
        onPress={() => void pick()}
        className="flex-row items-center gap-3 rounded-xl border border-gray-300 bg-white px-3.5 py-3"
      >
        {uri ? (
          <Image source={{ uri }} className="h-12 w-12 rounded-full bg-gray-100" />
        ) : (
          <View className="h-12 w-12 items-center justify-center rounded-full bg-gray-100">
            <Ionicons name="camera" size={20} color="#9ca3af" />
          </View>
        )}
        <Text className="text-sm text-gray-600">{uri ? 'Change photo' : 'Choose a photo'}</Text>
      </Pressable>
    </View>
  );
}
