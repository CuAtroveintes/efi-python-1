from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from app.db import get_session
from app.models.edificio import (
    Edificio,
    EdificioCreate,
    EdificioUpdate,
    EdificioPublic,
    EdificioPublicNested
)

router = APIRouter(
    prefix="/edificios",
    tags=["Edificios"]
)

SessionDep = Annotated[Session, Depends(get_session)]


# 1. CREATE
@router.post(
    "/",
    response_model=EdificioPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear edificio"
)
def create_edificio(edificio_data: EdificioCreate, session: SessionDep):
    db_edificio = Edificio.model_validate(edificio_data)
    session.add(db_edificio)
    session.commit()
    session.refresh(db_edificio)
    return db_edificio


# 2. READ ALL (Paginado)
@router.get(
    "/",
    response_model=Page[EdificioPublic],
    summary="Listar edificios"
)
def get_edificios(session: SessionDep):
    return paginate(session, select(Edificio))


# 3. READ ONE
@router.get(
    "/{edificio_id}",
    response_model=EdificioPublicNested,
    summary="Obtener edificio por ID",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Edificio no encontrado"}}
)
def get_edificio_by_id(edificio_id: int, session: SessionDep):
    edificio = session.get(Edificio, edificio_id)
    if not edificio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Edificio con ID {edificio_id} no encontrado"
        )
    return edificio


# 4. UPDATE
@router.patch(
    "/{edificio_id}",
    response_model=EdificioPublic,
    summary="Actualizar edificio",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Edificio no encontrado"}}
)
def update_edificio(edificio_id: int, edificio_data: EdificioUpdate, session: SessionDep):
    db_edificio = session.get(Edificio, edificio_id)
    if not db_edificio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Edificio con ID {edificio_id} no encontrado"
        )
    update_dict = edificio_data.model_dump(exclude_unset=True)
    db_edificio.sqlmodel_update(update_dict)
    session.add(db_edificio)
    session.commit()
    session.refresh(db_edificio)
    return db_edificio


# 5. DELETE
@router.delete(
    "/{edificio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar edificio",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Edificio no encontrado"}}
)
def delete_edificio(edificio_id: int, session: SessionDep):
    edificio = session.get(Edificio, edificio_id)
    if not edificio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Edificio con ID {edificio_id} no encontrado"
        )
    session.delete(edificio)
    session.commit()
    return None
