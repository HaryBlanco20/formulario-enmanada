import bcrypt
from sqlalchemy.orm import Session

from app.config import normalize_email, password_meets_policy
from app.models import User


def verify_password(plain: str, password_hash: str) -> bool:
    ok, _ = password_meets_policy(plain)
    if not ok:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def hash_password(plain: str) -> str:
    ok, msg = password_meets_policy(plain)
    if not ok:
        raise ValueError(msg)
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == normalize_email(email)).one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
