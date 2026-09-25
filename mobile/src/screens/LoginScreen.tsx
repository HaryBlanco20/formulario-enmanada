import { useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { StatusBar } from 'expo-status-bar';

import { useAuth } from '../auth/AuthContext';
import {
  PASSWORD_POLICY_HINT,
  validatePassword,
} from '../lib/passwordPolicy';
import { validateEmail } from '../lib/validateEmail';
import {
  FAMILY_USER_SLOTS,
  getAllowedEmails,
  isSupabaseConfigured,
  supabase,
} from '../lib/supabase';
import { colors } from '../theme/colors';

function mapAuthError(message: string): string {
  const lower = message.toLowerCase();
  if (lower.includes('invalid login credentials')) {
    return 'Correo o contraseña incorrectos.';
  }
  if (lower.includes('email not confirmed')) {
    return 'Confirma tu correo antes de iniciar sesión.';
  }
  return 'No se pudo iniciar sesión. Intenta de nuevo.';
}

export function LoginScreen() {
  const { refreshSession } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fieldError, setFieldError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async () => {
    setFieldError(null);

    if (!isSupabaseConfigured) {
      setFieldError(
        'Falta configurar Supabase. Copia .env.example a .env y reinicia Expo.'
      );
      return;
    }

    const emailError = validateEmail(email);
    if (emailError) {
      setFieldError(emailError);
      return;
    }

    const normalizedEmail = email.trim().toLowerCase();
    const allowed = getAllowedEmails();
    if (allowed && !allowed.includes(normalizedEmail)) {
      setFieldError('Este correo no está autorizado en la app familiar.');
      return;
    }

    const passwordResult = validatePassword(password);
    if (!passwordResult.ok) {
      setFieldError(passwordResult.message);
      return;
    }

    setSubmitting(true);
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: normalizedEmail,
        password,
      });
      if (error) {
        setFieldError(mapAuthError(error.message));
        return;
      }
      await refreshSession();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.root}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <StatusBar style="light" />
      <View style={styles.card}>
        <View style={styles.brandRow}>
          <View style={styles.logoMark}>
            <Text style={styles.logoLetter}>G</Text>
          </View>
          <View>
            <Text style={styles.title}>GymVe</Text>
            <Text style={styles.subtitle}>Acceso familiar privado</Text>
          </View>
        </View>

        <Text style={styles.hint}>
          Hasta {FAMILY_USER_SLOTS} usuarios con correo y contraseña.
        </Text>

        <Text style={styles.label}>Correo electrónico</Text>
        <TextInput
          style={styles.input}
          value={email}
          onChangeText={setEmail}
          autoCapitalize="none"
          autoCorrect={false}
          keyboardType="email-address"
          textContentType="username"
          placeholder="tu@correo.com"
          placeholderTextColor={colors.textSecondary}
          editable={!submitting}
        />

        <Text style={styles.label}>Contraseña</Text>
        <TextInput
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          secureTextEntry
          textContentType="password"
          placeholder="••••••••••"
          placeholderTextColor={colors.textSecondary}
          editable={!submitting}
        />
        <Text style={styles.policy}>{PASSWORD_POLICY_HINT}</Text>

        {fieldError ? <Text style={styles.error}>{fieldError}</Text> : null}

        <Pressable
          style={({ pressed }) => [
            styles.button,
            pressed && styles.buttonPressed,
            submitting && styles.buttonDisabled,
          ]}
          onPress={() => void onSubmit()}
          disabled={submitting}
        >
          {submitting ? (
            <ActivityIndicator color={colors.background} />
          ) : (
            <Text style={styles.buttonText}>Iniciar sesión</Text>
          )}
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: colors.background,
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderWidth: 0.5,
    borderColor: colors.surfaceBorder,
    padding: 24,
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    marginBottom: 8,
  },
  logoMark: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoLetter: {
    fontSize: 22,
    fontWeight: '500',
    color: colors.background,
  },
  title: {
    fontSize: 24,
    fontWeight: '500',
    color: colors.text,
  },
  subtitle: {
    fontSize: 13,
    color: colors.textSecondary,
    marginTop: 2,
  },
  hint: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 20,
  },
  label: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 6,
    marginTop: 12,
  },
  input: {
    backgroundColor: colors.inputBg,
    borderWidth: 0.5,
    borderColor: colors.surfaceBorder,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 15,
    color: colors.text,
  },
  policy: {
    fontSize: 11,
    color: colors.textSecondary,
    marginTop: 8,
    lineHeight: 16,
  },
  error: {
    fontSize: 13,
    color: colors.error,
    marginTop: 14,
  },
  button: {
    marginTop: 22,
    backgroundColor: colors.primary,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
  },
  buttonPressed: {
    backgroundColor: colors.primaryMuted,
  },
  buttonDisabled: {
    opacity: 0.7,
  },
  buttonText: {
    fontSize: 15,
    fontWeight: '500',
    color: colors.background,
  },
});
