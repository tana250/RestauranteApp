from typing import List

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Personal(Base):
    __tablename__ = "personal"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    dni: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    mozos: Mapped[List["Mozo"]] = relationship(back_populates="personal", lazy="selectin")
    consumos_personal: Mapped[List["ConsumoPersonal"]] = relationship(
        back_populates="personal", lazy="selectin"
    )

    def to_json(self):
        return {"id": self.id, "dni": self.dni, "nombre": self.nombre, "activo": bool(self.activo)}

    @classmethod
    def from_json(cls, data):
        for campo in ("dni", "nombre"):
            if campo not in data:
                raise KeyError(campo)
        activo = data.get("activo", True)
        if isinstance(activo, str):
            activo = activo.lower() == "true"
        return cls(dni=data["dni"], nombre=data["nombre"], activo=bool(activo))

    def update_from_json(self, data):
        if "dni" in data:
            self.dni = data["dni"]
        if "nombre" in data:
            self.nombre = data["nombre"]
        if "activo" in data:
            activo = data["activo"]
            if isinstance(activo, str):
                activo = activo.lower() == "true"
            self.activo = bool(activo)
