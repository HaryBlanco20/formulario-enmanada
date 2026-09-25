const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateEmail(email: string): string | null {
  const trimmed = email.trim();
  if (!trimmed) {
    return 'Ingresa tu correo electrónico.';
  }
  if (!EMAIL_REGEX.test(trimmed)) {
    return 'El correo electrónico no es válido.';
  }
  return null;
}
