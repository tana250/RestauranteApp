from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class TipoInsumo(Base):
    __tablename__ = "tipos_insumo"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tipo: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    insumos: Mapped[List["Insumo"]] = relationship(
        back_populates="tipo_insumo", lazy="selectin"
    )

    def to_json(self):
        return {"id": self.id, "tipo": self.tipo}

    @classmethod
    def from_json(cls, data):
        if "tipo" not in data:
            raise KeyError("tipo")
        return cls(tipo=data["tipo"])

    def update_from_json(self, data):
        if "tipo" in data:
            self.tipo = data["tipo"]
