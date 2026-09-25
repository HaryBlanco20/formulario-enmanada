/**
 * Política de contraseñas GymVe (familia, 4 usuarios).
 * - Mínimo 10 caracteres
 * - Al menos un carácter especial (no alfanumérico)
 */
export const PASSWORD_MIN_LENGTH = 10;

/** Caracteres especiales aceptados (cualquier símbolo que no sea letra ni dígito). */
export const PASSWORD_SPECIAL_CHAR_REGEX = /[^A-Za-z0-9]/;

/** Validación completa en una sola expresión (referencia / tests). */
export const PASSWORD_POLICY_REGEX = /^(?=.*[^A-Za-z0-9]).{10,}$/;

export type PasswordValidationResult =
  | { ok: true }
  | { ok: false; message: string };

export function validatePassword(password: string): PasswordValidationResult {
  if (password.length < PASSWORD_MIN_LENGTH) {
    return {
      ok: false,
      message: `La contraseña debe tener al menos ${PASSWORD_MIN_LENGTH} caracteres.`,
    };
  }
  if (!PASSWORD_SPECIAL_CHAR_REGEX.test(password)) {
    return {
      ok: false,
      message:
        'La contraseña debe incluir al menos un carácter especial (por ejemplo: ! @ # $ % & *).',
    };
  }
  return { ok: true };
}

export const PASSWORD_POLICY_HINT =
  'Mínimo 10 caracteres e incluir al menos un carácter especial (! @ # …).';
