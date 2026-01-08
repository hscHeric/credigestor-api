from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.system_config import SystemConfig


def get_or_create_system_config(db: Session) -> SystemConfig:
    cfg = db.query(SystemConfig).order_by(SystemConfig.id.asc()).first()
    if cfg:
        return cfg

    cfg = SystemConfig()
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg
