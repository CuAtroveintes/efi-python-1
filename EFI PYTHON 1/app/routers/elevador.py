from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from app.db import get_session
from app.models.edificio import Edificio
from app.models.elevador import (
    Elevador,
    ElevadorCreate,
    ElevadorUpdate,
    ElevadorPublic,
    ElevadorPublicNested
)

router = APIRouter(
    prefix="/elevadores",
    tags=["Elevadores"]
)

SessionDep = Annotated[Session, Depends(get_session)]


# 1. CREATE
@router.post(
    "/",
    response_model=ElevadorPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear elevador",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "El edificio asociado no existe"}
    }
)
def create_elevador(elevador_data: ElevadorCreate, session: SessionDep):
    edificio = session.get(Edificio, elevador_data.edificio_id)
    if not edificio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se puede crear el elevador. Edificio con ID {elevador_data.edificio_id} no encontrado"
        )

    db_elevador = Elevador.model_validate(elevador_data)
    session.add(db_elevador)
    session.commit()
    session.refresh(db_elevador)
    return db_elevador


# 2. READ ALL (Paginado)
@router.get(
    "/",
    response_model=Page[ElevadorPublic],
    summary="Listar elevadores"
)
def get_elevadores(session: SessionDep):
    return paginate(session, select(Elevador))


# 3. READ ONE
@router.get(
    "/{elevador_id}",
    response_model=ElevadorPublicNested,
    summary="Obtener elevador por ID",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Elevador no encontrado"}}
)
def get_elevador_by_id(elevador_id: int, session: SessionDep):
    elevador = session.get(Elevador, elevador_id)
    if not elevador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Elevador con ID {elevador_id} no encontrado"
        )
    return elevador


# 4. UPDATE
@router.patch(
    "/{elevador_id}",
    response_model=ElevadorPublic,
    summary="Actualizar elevador",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Elevador o edificio no encontrado"}
    }
)
def update_elevador(elevador_id: int, elevador_data: ElevadorUpdate, session: SessionDep):
    db_elevador = session.get(Elevador, elevador_id)
    if not db_elevador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Elevador con ID {elevador_id} no encontrado"
        )

    if elevador_data.edificio_id is not None:
        edificio = session.get(Edificio, elevador_data.edificio_id)
        if not edificio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Edificio con ID {elevador_data.edificio_id} no encontrado"
            )

    update_dict = elevador_data.model_dump(exclude_unset=True)
    db_elevador.sqlmodel_update(update_dict)
    session.add(db_elevador)
    session.commit()
    session.refresh(db_elevador)
    return db_elevador


# 5. DELETE
@router.delete(
    "/{elevador_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar elevador",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Elevador no encontrado"}}
)
def delete_elevador(elevador_id: int, session: SessionDep):
    elevador = session.get(Elevador, elevador_id)
    if not elevador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Elevador con ID {elevador_id} no encontrado"
        )
    session.delete(elevador)
    session.commit()
    return None
