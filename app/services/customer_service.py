from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate


def get_customer_by_cpf(db: Session, cpf: str) -> Customer | None:
    return db.query(Customer).filter(Customer.cpf == cpf).first()


def get_customer_by_id(db: Session, customer_id: int) -> Customer | None:
    return db.query(Customer).filter(Customer.id == customer_id).first()


def list_customers(db: Session) -> list[Customer]:
    return db.query(Customer).order_by(Customer.full_name.asc()).all()


def create_customer(db: Session, data: CustomerCreate) -> Customer:
    if get_customer_by_cpf(db, data.cpf):
        raise ValueError("MSG05: O CPF informado já pertence a outro cliente.")

    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update_customer(db: Session, customer: Customer, data: CustomerUpdate) -> Customer:
    payload = data.model_dump(exclude_unset=True)

    for field, value in payload.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer
