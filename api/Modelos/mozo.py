from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Mozo(Base):
    __tablename__ = "mozo"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    personalId: Mapped[int] = mapped_column(
        ForeignKey("personal.id"), nullable=False, unique=True
    )

    personal: Mapped["Personal"] = relationship(back_populates="mozos", lazy="selectin")
    ventas: Mapped[List["Venta"]] = relationship(back_populates="mozo", lazy="selectin")

    def to_json(self):
        return {"id": self.id, "personalId": self.personalId}

    @classmethod
    def from_json(cls, data):
        if "personalId" not in data:
            raise KeyError("personalId")
        return cls(personalId=data["personalId"])

    def update_from_json(self, data):
        if "personalId" in data:
            self.personalId = data["personalId"]
