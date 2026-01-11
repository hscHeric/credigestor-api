"""
Script para criar usuário administrador inicial (DEV)

Cria o usuário admin padrão se não existir:
- Email: admin@credigestor.com
- Senha: admin_credigestor

Uso:
  python scripts/create_admin.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy.exc import SQLAlchemyError  # noqa: E402

from app.database import SessionLocal, engine, Base  # noqa: E402

# Importar todos os models para registrar no metadata
import app.models  # noqa: E402, F401

from app.models.user import User, UserRole  # noqa: E402
from app.services.auth_service import hash_password  # noqa: E402


ADMIN_EMAIL = "admin@credigestor.com"
ADMIN_PASSWORD = "admin_credigestor"
ADMIN_NAME = "Administrador"


def create_admin_user() -> None:
    """Cria usuário admin padrão se não existir (idempotente)."""

    print("Verificando/criando tabelas no banco de dados...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tabelas verificadas/criadas com sucesso!")
    except SQLAlchemyError as e:
        print(f"✗ Erro ao criar/verificar tabelas: {e}")
        return

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if admin:
            print("Usuário admin já existe!")
            print(f"Email: {ADMIN_EMAIL}")
            return

        admin = User(
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            password_hash=hash_password(ADMIN_PASSWORD),
            role=UserRole.ADMIN.value,
            active=True,
            temporary_password=True,
        )

        db.add(admin)
        db.commit()

        print("✓ Usuário admin criado com sucesso!")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Senha: {ADMIN_PASSWORD}")
        print("IMPORTANTE: Troque a senha após o primeiro login!")

    except SQLAlchemyError as e:
        db.rollback()
        print(f"✗ Erro ao criar admin: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
