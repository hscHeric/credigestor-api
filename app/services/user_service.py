from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.services.auth_service import hash_password


def create_user(db: Session, data: UserCreate) -> User:
    # e-mail único
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise ValueError("MSG20: O e-mail informado já está em uso.")

    # senha padrão = email
    password_hash = hash_password(str(data.email))

    user = User(
        name=data.name,
        email=data.email,
        password_hash=password_hash,
        role=data.role,
        active=data.active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id.asc()).all()


def update_user(db: Session, user_id: int, data: UserUpdate) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Usuário não encontrado.")

    payload = data.model_dump(exclude_unset=True)

    # reset de senha para email (opcional)
    if payload.pop("reset_password_to_email", False):
        user.password_hash = hash_password(str(user.email))

    for k, v in payload.items():
        setattr(user, k, v)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("Usuário não encontrado.")

    user.active = False
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
