from datetime import date
from typing import List

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Venta(Base):
    __tablename__ = "venta"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    mozoId: Mapped[int] = mapped_column(ForeignKey("mozo.id"), nullable=False)
    mesaId: Mapped[int] = mapped_column(ForeignKey("mesa.id"), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)

    mozo: Mapped["Mozo"] = relationship(back_populates="ventas", lazy="selectin")
    mesa: Mapped["Mesa"] = relationship(back_populates="ventas", lazy="selectin")
    producto_ventas: Mapped[List["ProductoVenta"]] = relationship(
        back_populates="venta", lazy="selectin"
    )
    pagos: Mapped[List["Pago"]] = relationship(back_populates="venta", lazy="selectin")

    def to_json(self):
        return {
            "id": self.id,
            "mozoId": self.mozoId,
            "mesaId": self.mesaId,
            "fecha": self.fecha.isoformat() if self.fecha is not None else None,
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("mozoId", "mesaId", "fecha"):
            if campo not in data:
                raise KeyError(campo)
        fecha = data["fecha"]
        if isinstance(fecha, str):
            fecha = date.fromisoformat(fecha)
        return cls(mozoId=data["mozoId"], mesaId=data["mesaId"], fecha=fecha)

    def update_from_json(self, data):
        if "mozoId" in data:
            self.mozoId = data["mozoId"]
        if "mesaId" in data:
            self.mesaId = data["mesaId"]
        if "fecha" in data:
            fecha = data["fecha"]
            if isinstance(fecha, str):
                fecha = date.fromisoformat(fecha)
            self.fecha = fecha
