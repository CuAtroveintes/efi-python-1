from typing import Annotated, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.edificio import Edificio
    from app.models.mantenimiento import Mantenimiento


# 1. BASE
class ElevadorBase(SQLModel):
    serial_number: Annotated[str, Field(min_length=3, max_length=50, index=True)]
    brand: Annotated[str, Field(description="Ej: Otis, Schindler, ThyssenKrupp")]
    capacity_kg: Annotated[int, Field(ge=100, le=5000, description="Capacidad máxima en KG")]


# 2. TABLE
class Elevador(ElevadorBase, table=True):
    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    edificio_id: Annotated[int, Field(foreign_key="edificio.id", index=True)]

    edificio: Optional["Edificio"] = Relationship(back_populates="elevadores")
    mantenimientos: list["Mantenimiento"] = Relationship(
        back_populates="elevador",
        cascade_delete=True
    )


# 3. SCHEMAS DE ENTRADA
class ElevadorCreate(ElevadorBase):
    edificio_id: int


class ElevadorUpdate(SQLModel):
    serial_number: Annotated[Optional[str], Field(default=None)]
    brand: Annotated[Optional[str], Field(default=None)]
    capacity_kg: Annotated[Optional[int], Field(default=None)]
    edificio_id: Annotated[Optional[int], Field(default=None)]


# 4. PUBLIC
class ElevadorPublic(ElevadorBase):
    id: int
    edificio_id: int


# 5. NESTED
from app.models.edificio import EdificioPublic


class ElevadorPublicNested(ElevadorPublic):
    edificio: Optional[EdificioPublic] = None


# Reconstrucción de modelo para resolver OpenAPI
ElevadorPublicNested.model_rebuild()
