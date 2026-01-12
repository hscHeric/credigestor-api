from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.router.auth_routes import get_current_user
from app.schemas.sale_schema import SaleCreate, SaleWithNotesOut, SaleUpdate
from app.services.sale_service import (
    create_sale_and_promissory_notes,
    get_sales,
    get_sale_by_id,
    delete_sale,
    update_sale
)

router = APIRouter()


@router.post(
    "",
    response_model=SaleWithNotesOut,
    status_code=status.HTTP_201_CREATED,
)
def create_sale_endpoint(
    data: SaleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Cria uma nova venda e suas notas promissórias.
    """
    try:
        sale, notes = create_sale_and_promissory_notes(db, user_id=user.id, data=data)
        # Injeta relação no retorno
        sale.promissory_notes = notes
        return sale
    except ValueError as e:
        msg = str(e)
        # Cliente não encontrado -> 404
        if "Cliente não encontrado" in msg:
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)


@router.get(
    "",
    response_model=List[SaleWithNotesOut],
    status_code=status.HTTP_200_OK,
)
def list_sales_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    client_name: Optional[str] = Query(None, description="Filtrar por nome do cliente"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Lista todas as vendas. Permite paginação e filtro por nome do cliente.
    """
    sales = get_sales(
        db, 
        skip=skip, 
        limit=limit, 
        user_id=None,
        client_name=client_name
    )
    return sales


@router.get(
    "/{sale_id}",
    response_model=SaleWithNotesOut,
    status_code=status.HTTP_200_OK,
)
def get_sale_endpoint(
    sale_id: int = Path(..., description="ID da venda"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Busca uma venda específica pelo ID.
    """
    sale = get_sale_by_id(db, sale_id=sale_id)
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Venda não encontrada."
        )
    return sale


@router.put(
    "/{sale_id}",
    response_model=SaleWithNotesOut,
    status_code=status.HTTP_200_OK,
)
def update_sale_endpoint(
    data: SaleUpdate,
    sale_id: int = Path(..., description="ID da venda"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Atualiza uma venda. Se alterar valores financeiros, regenera as notas
    (desde que nenhuma tenha sido paga).
    """
    try:
        sale, notes = update_sale(db, sale_id=sale_id, data=data)
        sale.promissory_notes = notes
        return sale
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{sale_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_sale_endpoint(
    sale_id: int = Path(..., description="ID da venda"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Deleta uma venda e suas notas promissórias.
    """
    success = delete_sale(db, sale_id=sale_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Venda não encontrada."
        )
    return None