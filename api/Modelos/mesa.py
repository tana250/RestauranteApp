from typing import List

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Mesa(Base):
    __tablename__ = "mesa"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    numero: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    ventas: Mapped[List["Venta"]] = relationship(back_populates="mesa", lazy="selectin")

    def to_json(self):
        return {"id": self.id, "numero": self.numero}

    @classmethod
    def from_json(cls, data):
        if "numero" not in data:
            raise KeyError("numero")
        return cls(numero=data["numero"])

    def update_from_json(self, data):
        if "numero" in data:
            self.numero = data["numero"]
