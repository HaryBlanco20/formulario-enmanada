import { ActivityIndicator, StyleSheet, View } from 'react-native';

import { AuthProvider, useAuth } from './src/auth/AuthContext';
import { LoginScreen } from './src/screens/LoginScreen';
import { HomeScreen } from './src/screens/HomeScreen';
import { colors } from './src/theme/colors';

function RootNavigator() {
  const { session, loading } = useAuth();

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!session) {
    return <LoginScreen />;
  }

  return <HomeScreen />;
}

export default function App() {
  return (
    <AuthProvider>
      <RootNavigator />
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  loading: {
    flex: 1,
    backgroundColor: colors.background,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
