from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from app.db import get_session
from app.models.elevador import Elevador
from app.models.mantenimiento import (
    Mantenimiento,
    MantenimientoCreate,
    MantenimientoUpdate,
    MantenimientoPublic,
    MantenimientoPublicNested
)

router = APIRouter(
    prefix="/mantenimientos",
    tags=["Mantenimientos"]
)

SessionDep = Annotated[Session, Depends(get_session)]


# 1. CREATE
@router.post(
    "/",
    response_model=MantenimientoPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo mantenimiento",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "El elevador asociado no existe"}
    }
)
def create_mantenimiento(mantenimiento_data: MantenimientoCreate, session: SessionDep):
    elevador = session.get(Elevador, mantenimiento_data.elevador_id)
    if not elevador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se puede programar mantenimiento. Elevador con ID {mantenimiento_data.elevador_id} no encontrado"
        )

    db_mantenimiento = Mantenimiento.model_validate(mantenimiento_data)
    session.add(db_mantenimiento)
    session.commit()
    session.refresh(db_mantenimiento)
    return db_mantenimiento


# 2. READ ALL (Paginado)
@router.get(
    "/",
    response_model=Page[MantenimientoPublic],
    summary="Listar mantenimientos"
)
def get_mantenimientos(session: SessionDep):
    return paginate(session, select(Mantenimiento))


# 3. READ ONE
@router.get(
    "/{mantenimiento_id}",
    response_model=MantenimientoPublicNested,
    summary="Obtener mantenimiento por ID",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Mantenimiento no encontrado"}
    }
)
def get_mantenimiento_by_id(mantenimiento_id: int, session: SessionDep):
    mantenimiento = session.get(Mantenimiento, mantenimiento_id)
    if not mantenimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mantenimiento con ID {mantenimiento_id} no encontrado"
        )
    return mantenimiento


# 4. UPDATE
@router.patch(
    "/{mantenimiento_id}",
    response_model=MantenimientoPublic,
    summary="Actualizar mantenimiento",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Mantenimiento o elevador no encontrado"}
    }
)
def update_mantenimiento(
    mantenimiento_id: int,
    mantenimiento_data: MantenimientoUpdate,
    session: SessionDep
):
    db_mantenimiento = session.get(Mantenimiento, mantenimiento_id)
    if not db_mantenimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mantenimiento con ID {mantenimiento_id} no encontrado"
        )

    if mantenimiento_data.elevador_id is not None:
        elevador = session.get(Elevador, mantenimiento_data.elevador_id)
        if not elevador:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Elevador con ID {mantenimiento_data.elevador_id} no encontrado"
            )

    update_dict = mantenimiento_data.model_dump(exclude_unset=True)
    db_mantenimiento.sqlmodel_update(update_dict)
    session.add(db_mantenimiento)
    session.commit()
    session.refresh(db_mantenimiento)
    return db_mantenimiento


# 5. DELETE
@router.delete(
    "/{mantenimiento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar mantenimiento",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Mantenimiento no encontrado"}
    }
)
def delete_mantenimiento(mantenimiento_id: int, session: SessionDep):
    mantenimiento = session.get(Mantenimiento, mantenimiento_id)
    if not mantenimiento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mantenimiento con ID {mantenimiento_id} no encontrado"
        )
    session.delete(mantenimiento)
    session.commit()
    return None
