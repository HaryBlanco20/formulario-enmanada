#!/usr/bin/env python3
"""Genera un hash bcrypt para pegar en .env (nunca guardes la contraseña en texto plano en el repo)."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.auth import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description="Hash bcrypt para GymVe (.env)")
    parser.add_argument("password", nargs="?", help="Contraseña (si se omite, se pide sin eco)")
    args = parser.parse_args()
    if args.password:
        plain = args.password
    else:
        import getpass

        plain = getpass.getpass("Contraseña: ")
        confirm = getpass.getpass("Repetir: ")
        if plain != confirm:
            print("No coinciden.", file=sys.stderr)
            sys.exit(1)
    try:
        hashed = hash_password(plain)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    print(hashed)


if __name__ == "__main__":
    main()
