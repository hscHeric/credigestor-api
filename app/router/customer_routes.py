from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.router.auth_routes import get_current_user
from app.models.user import User
from app.services.customer_service import (
    create_customer,
    get_customer_by_id,
    list_customers,
    update_customer,
)
from app.schemas.customer_schema import (
    CustomerCreate,
    CustomerUpdate,
    CustomerOut,
)

router = APIRouter()


@router.post(
    "",
    response_model=CustomerOut,
    status_code=status.HTTP_201_CREATED,
)
def create(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return create_customer(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[CustomerOut])
def list_all(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return list_customers(db)


@router.get("/{customer_id}", response_model=CustomerOut)
def get_one(
    customer_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return customer


@router.put("/{customer_id}", response_model=CustomerOut)
def update(
    customer_id: int,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    customer = get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    return update_customer(db, customer, data)
