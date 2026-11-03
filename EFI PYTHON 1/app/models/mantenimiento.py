from datetime import datetime, timezone
from typing import Annotated, Optional, TYPE_CHECKING
from pydantic import field_validator
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.elevador import Elevador


class MantenimientoBase(SQLModel):
    scheduled_date: Annotated[datetime, Field(description="Fecha y hora programada")]
    description: Annotated[str, Field(min_length=5, max_length=255)]
    status: Annotated[str, Field(default="Pendiente")]

    @field_validator("scheduled_date")
    @classmethod
    def ensure_timezone(cls, v: datetime) -> datetime:
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class Mantenimiento(MantenimientoBase, table=True):
    id: Annotated[Optional[int], Field(default=None, primary_key=True)]
    elevador_id: Annotated[int, Field(foreign_key="elevador.id", index=True)]

    elevador: Optional["Elevador"] = Relationship(back_populates="mantenimientos")


class MantenimientoCreate(MantenimientoBase):
    elevador_id: int


class MantenimientoUpdate(SQLModel):
    scheduled_date: Annotated[Optional[datetime], Field(default=None)]
    description: Annotated[Optional[str], Field(default=None)]
    status: Annotated[Optional[str], Field(default=None)]
    elevador_id: Annotated[Optional[int], Field(default=None)]

    @field_validator("scheduled_date")
    @classmethod
    def ensure_timezone(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v


class MantenimientoPublic(MantenimientoBase):
    id: int
    elevador_id: int


from app.models.elevador import ElevadorPublic


class MantenimientoPublicNested(MantenimientoPublic):
    elevador: Optional[ElevadorPublic] = None


# Reconstrucción de modelo para resolver OpenAPI
MantenimientoPublicNested.model_rebuild()
