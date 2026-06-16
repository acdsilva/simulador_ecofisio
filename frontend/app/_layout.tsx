import { Stack } from 'expo-router';
import { LanguageProvider } from '../contexts/LanguageContext';

export default function RootLayout() {
  return (
    <LanguageProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="index" />
        <Stack.Screen name="species" />
        <Stack.Screen name="simulator" />
      </Stack>
    </LanguageProvider>
  );
}
