from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class MetodoPago(Base):
    __tablename__ = "metodosPago"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    metodo: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    pagos: Mapped[List["Pago"]] = relationship(back_populates="metodo_pago", lazy="selectin")

    def to_json(self):
        return {"id": self.id, "metodo": self.metodo}

    @classmethod
    def from_json(cls, data):
        if "metodo" not in data:
            raise KeyError("metodo")
        return cls(metodo=data["metodo"])

    def update_from_json(self, data):
        if "metodo" in data:
            self.metodo = data["metodo"]
