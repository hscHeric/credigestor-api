"""
Script para criar usuário administrador inicial
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.utils.security import hash_password

# Importar todos os models para garantir que sejam registrados
from app.models import User, Customer, Sale, PromissoryNote, Payment, SystemConfig


def create_admin_user():
    """Cria usuário admin padrão se não existir"""

    print("Criando tabelas no banco de dados...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✓ Tabelas verificadas/criadas com sucesso!")
    except Exception as e:
        print(f"✗ Erro ao criar tabelas: {e}")
        return

    # Agora criar o usuário admin
    db = SessionLocal()

    try:
        # Verificar se já existe admin
        admin = db.query(User).filter(User.email == "admin@credigestor.com").first()

        if admin:
            print("Usuário admin já existe!")
            print("Email: admin@credigestor.com")
            return

        # Criar admin - usar string "admin" em vez de enum
        admin = User(
            name="Administrador",
            email="admin@credigestor.com",
            password_hash=hash_password("admin123"),
            role="admin",
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

