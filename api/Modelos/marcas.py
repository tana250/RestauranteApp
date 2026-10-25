from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Marca(Base):
    __tablename__ = "marcas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    insumos: Mapped[List["Insumo"]] = relationship(
        back_populates="marca", lazy="selectin"
    )

    def to_json(self):
        return {"id": self.id, "nombre": self.nombre}

    @classmethod
    def from_json(cls, data):
        if "nombre" not in data:
            raise KeyError("nombre")
        return cls(nombre=data["nombre"])

    def update_from_json(self, data):
        if "nombre" in data:
            self.nombre = data["nombre"]
