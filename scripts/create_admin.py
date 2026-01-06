"""
Script para criar usuário administrador inicial
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import hash_password


def create_admin_user():
    """Cria usuário admin padrão se não existir"""
    db = SessionLocal()

    try:
        # Verificar se já existe admin
        admin = db.query(User).filter(User.email == "admin@credigestor.com").first()

        if admin:
            print("Usuário admin já existe!")
            print("Email: admin@credigestor.com")
            return

        # Criar admin
        admin = User(
            name="Administrador",
            email="admin@credigestor.com",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
            active=True,
            temporary_password=True,
        )

        db.add(admin)
        db.commit()

        print("Usuário admin criado com sucesso!")
        print("Email: admin@credigestor.com")
        print("Senha: admin123")
        print("IMPORTANTE: Troque a senha após o primeiro login!")

    except Exception as e:
        print(f"✗ Erro ao criar admin: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_admin_user()
