from typing import Annotated, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.elevador import Elevador, ElevadorPublic


# 1. BASE
class EdificioBase(SQLModel):
    name: Annotated[str, Field(min_length=2, max_length=100, index=True)]
    address: Annotated[str, Field(min_length=5, max_length=200)]
    floors: Annotated[int, Field(ge=1, description="Cantidad de pisos")]


# 2. TABLE
class Edificio(EdificioBase, table=True):
    id: Annotated[Optional[int], Field(default=None, primary_key=True)]

    elevadores: list["Elevador"] = Relationship(
        back_populates="edificio",
        cascade_delete=True
    )


# 3. SCHEMAS DE ENTRADA
class EdificioCreate(EdificioBase):
    pass


class EdificioUpdate(SQLModel):
    name: Annotated[Optional[str], Field(default=None)]
    address: Annotated[Optional[str], Field(default=None)]
    floors: Annotated[Optional[int], Field(default=None)]


# 4. PUBLIC
class EdificioPublic(EdificioBase):
    id: int


# 5. NESTED
from app.models.elevador import ElevadorPublic


class EdificioPublicNested(EdificioPublic):
    elevadores: list[ElevadorPublic] = []


# Reconstrucción de modelo para resolver OpenAPI
EdificioPublicNested.model_rebuild()
