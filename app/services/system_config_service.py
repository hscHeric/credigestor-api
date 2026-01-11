from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.system_config import SystemConfig
from app.schemas.system_config_schema import SystemConfigUpdate


def get_or_create_system_config(db: Session) -> SystemConfig:
    cfg = db.query(SystemConfig).order_by(SystemConfig.id.asc()).first()
    if cfg:
        return cfg

    cfg = SystemConfig()
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg


def update_system_config(db: Session, data: SystemConfigUpdate) -> SystemConfig:
    cfg = get_or_create_system_config(db)

    payload = data.model_dump(exclude_unset=True)
    for k, v in payload.items():
        setattr(cfg, k, v)

    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return cfg

