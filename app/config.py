import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

SPECIAL_CHARACTERS = set("!@#$%^&*()_+-=[]{}|;:',.<>?/`~\"\\")

KNOWN_WEAK_SECRETS = frozenset(
    {
        "",
        "cambia-esto-por-un-secreto-largo-y-aleatorio-de-al-menos-32",
        "change-me",
        "dev-secret-change-me-in-production-min-32-chars",
        "gymve",
        "secret",
        "session_secret",
    }
)

DEFAULT_POSTGRES_PASSWORDS = frozenset({"gymve", "postgres", "changeme"})


@dataclass(frozen=True)
class SeedUserSpec:
    email: str
    password_hash: str | None
    plain_password: str | None
    display_name: str


def get_gymve_env() -> str:
    return os.getenv("GYMVE_ENV", "development").strip().lower()


def is_production() -> bool:
    return get_gymve_env() in ("production", "prod")


def password_meets_policy(password: str) -> tuple[bool, str]:
    if len(password) < 10:
        return False, "La contraseña debe tener al menos 10 caracteres."
    if not any(c in SPECIAL_CHARACTERS for c in password):
        return False, "La contraseña debe incluir al menos un carácter especial."
    return True, ""


def normalize_email(email: str) -> str:
    return email.strip().lower()


def get_database_url() -> str:
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://gymve_app:gymve_app_dev_only@localhost:5432/gymve",
    ).strip()
    if not url:
        raise RuntimeError("DATABASE_URL no está configurada.")
    return url


def _secret_from_env(name: str) -> str:
    return os.getenv(name, "").strip()


def validate_security_config() -> None:
    """Fallar al arrancar en producción si la configuración es insegura."""
    session = _secret_from_env("SESSION_SECRET")
    jwt = _secret_from_env("JWT_SECRET")

    if is_production():
        if len(session) < 32 or session.lower() in KNOWN_WEAK_SECRETS:
            raise RuntimeError(
                "En GYMVE_ENV=production, SESSION_SECRET debe ser aleatorio (≥32 caracteres) "
                "y distinto de valores de ejemplo."
            )
        if jwt and (len(jwt) < 32 or jwt.lower() in KNOWN_WEAK_SECRETS):
            raise RuntimeError(
                "En GYMVE_ENV=production, JWT_SECRET debe ser aleatorio (≥32 caracteres)."
            )
        origins = get_cors_origins()
        if not origins or "*" in origins:
            raise RuntimeError(
                "En GYMVE_ENV=production, CORS_ORIGINS debe listar orígenes explícitos "
                "(PWA iPhone + URL del API), sin '*'."
            )
        if os.getenv("GYMVE_ALLOW_INSECURE_DEV", "").strip().lower() in ("1", "true", "yes"):
            raise RuntimeError(
                "GYMVE_ALLOW_INSECURE_DEV no puede estar activo en producción."
            )
    elif len(session) < 32:
        raise RuntimeError("SESSION_SECRET debe tener al menos 32 caracteres.")


def get_session_secret() -> str:
    validate_security_config()
    secret = _secret_from_env("SESSION_SECRET")
    if len(secret) < 32:
        raise RuntimeError("SESSION_SECRET debe tener al menos 32 caracteres.")
    return secret


def get_jwt_secret() -> str:
    secret = _secret_from_env("JWT_SECRET")
    if len(secret) >= 32:
        return secret
    return get_session_secret()


def session_https_only() -> bool:
    if is_production():
        return True
    return os.getenv("GYMVE_SESSION_HTTPS_ONLY", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def get_app_host() -> str:
    return os.getenv("GYMVE_HOST", "0.0.0.0")


def get_app_port() -> int:
    return int(os.getenv("GYMVE_PORT", "8000"))


def get_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return ["*"]
    return [part.strip() for part in raw.split(",") if part.strip()]


def get_login_rate_limit() -> str:
    return os.getenv("GYMVE_LOGIN_RATE_LIMIT", "10/minute").strip()


def load_seed_users() -> list[SeedUserSpec]:
    """Usuarios para scripts/seed_users.py (hashes o contraseñas solo en .env local)."""
    users_json = os.getenv("GYMVE_USERS_JSON", "").strip()
    if users_json:
        try:
            raw = json.loads(users_json)
        except json.JSONDecodeError as exc:
            raise RuntimeError("GYMVE_USERS_JSON no es JSON válido.") from exc
        specs: list[SeedUserSpec] = []
        for i, item in enumerate(raw, start=1):
            email = normalize_email(str(item.get("email", "")))
            password_hash = str(item.get("password_hash", "")).strip() or None
            plain = str(item.get("password", "")).strip() or None
            display_name = str(item.get("display_name", f"Usuario {i}")).strip()
            if not email or (not password_hash and not plain):
                raise RuntimeError(f"Usuario #{i} en GYMVE_USERS_JSON incompleto.")
            specs.append(
                SeedUserSpec(email, password_hash, plain, display_name)
            )
        return specs

    specs = []
    for i in range(1, 5):
        email = normalize_email(os.getenv(f"GYMVE_USER_{i}_EMAIL", ""))
        password_hash = os.getenv(f"GYMVE_USER_{i}_PASSWORD_HASH", "").strip() or None
        plain = os.getenv(f"GYMVE_USER_{i}_PASSWORD", "").strip() or None
        display_name = os.getenv(f"GYMVE_USER_{i}_NAME", f"Familia {i}").strip()
        if email and (password_hash or plain):
            specs.append(SeedUserSpec(email, password_hash, plain, display_name))
    if not specs:
        raise RuntimeError(
            "Define usuarios para seed en .env (GYMVE_USER_1_* … GYMVE_USER_4_* "
            "con PASSWORD_HASH o PASSWORD solo en tu .env local)."
        )
    return specs
