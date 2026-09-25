#!/usr/bin/env python3
"""Inserta o actualiza los 4 usuarios familiares desde .env (hashes bcrypt)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.auth import hash_password
from app.config import load_seed_users, normalize_email
from app.db import Base, SessionLocal, engine
from app.models import User


def main() -> None:
    Base.metadata.create_all(bind=engine)
    specs = load_seed_users()
    db = SessionLocal()
    try:
        for spec in specs:
            if spec.password_hash:
                pwd_hash = spec.password_hash
            elif spec.plain_password:
                pwd_hash = hash_password(spec.plain_password)
            else:
                raise RuntimeError(f"Sin hash ni contraseña para {spec.email}")

            existing = (
                db.query(User).filter(User.email == normalize_email(spec.email)).one_or_none()
            )
            if existing:
                existing.password_hash = pwd_hash
                existing.display_name = spec.display_name
                print(f"Actualizado: {spec.email}")
            else:
                db.add(
                    User(
                        email=normalize_email(spec.email),
                        password_hash=pwd_hash,
                        display_name=spec.display_name,
                    )
                )
                print(f"Creado: {spec.email}")
        db.commit()
        count = db.query(User).count()
        print(f"Total usuarios en base de datos: {count}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
