import { Pressable, StyleSheet, Text, View } from 'react-native';
import { StatusBar } from 'expo-status-bar';

import { useAuth } from '../auth/AuthContext';
import { colors } from '../theme/colors';

export function HomeScreen() {
  const { user, signOut } = useAuth();

  return (
    <View style={styles.root}>
      <StatusBar style="light" />
      <Text style={styles.title}>Sesión activa</Text>
      <Text style={styles.email}>{user?.email ?? 'Usuario'}</Text>
      <Text style={styles.stub}>
        Próximamente: rutinas, progreso y más. Por ahora solo inicio de sesión.
      </Text>
      <Pressable
        style={({ pressed }) => [styles.button, pressed && styles.buttonPressed]}
        onPress={() => void signOut()}
      >
        <Text style={styles.buttonText}>Cerrar sesión</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.background,
    padding: 28,
    justifyContent: 'center',
  },
  title: {
    fontSize: 22,
    fontWeight: '500',
    color: colors.text,
    marginBottom: 8,
  },
  email: {
    fontSize: 15,
    color: colors.primary,
    marginBottom: 20,
  },
  stub: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 21,
    marginBottom: 28,
  },
  button: {
    alignSelf: 'flex-start',
    borderWidth: 0.5,
    borderColor: colors.surfaceBorder,
    borderRadius: 10,
    paddingVertical: 12,
    paddingHorizontal: 18,
  },
  buttonPressed: {
    backgroundColor: colors.surface,
  },
  buttonText: {
    fontSize: 14,
    color: colors.text,
  },
});
