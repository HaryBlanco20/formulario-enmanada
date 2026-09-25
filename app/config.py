import json
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

SPECIAL_CHARACTERS = set("!@#$%^&*()_+-=[]{}|;:',.<>?/`~\"\\")


@dataclass(frozen=True)
class SeedUserSpec:
    email: str
    password_hash: str | None
    plain_password: str | None
    display_name: str


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
        "postgresql+psycopg://gymve:gymve@localhost:5432/gymve",
    ).strip()
    if not url:
        raise RuntimeError("DATABASE_URL no está configurada.")
    return url


def get_session_secret() -> str:
    secret = os.getenv("SESSION_SECRET", "").strip()
    if len(secret) < 32:
        raise RuntimeError("SESSION_SECRET debe tener al menos 32 caracteres.")
    return secret


def get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "").strip()
    if len(secret) >= 32:
        return secret
    return get_session_secret()


def get_app_host() -> str:
    return os.getenv("GYMVE_HOST", "0.0.0.0")


def get_app_port() -> int:
    return int(os.getenv("GYMVE_PORT", "8000"))


def get_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return ["*"]
    return [part.strip() for part in raw.split(",") if part.strip()]


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
