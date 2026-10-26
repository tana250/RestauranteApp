from decimal import Decimal
from typing import List

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class EgresoMercaderia(Base):
    __tablename__ = "egreso_mercaderia"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ingresoMercaderiaId: Mapped[int] = mapped_column(
        ForeignKey("ingreso_mercaderia.id"), nullable=False
    )
    cantidad: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)

    ingreso_mercaderia: Mapped["IngresoMercaderia"] = relationship(
        lazy="selectin"
    )
    producto_ventas: Mapped[List["ProductoVenta"]] = relationship(
        back_populates="egreso_mercaderia", lazy="selectin"
    )
    consumos_personal: Mapped[List["ConsumoPersonal"]] = relationship(
        back_populates="egreso_mercaderia", lazy="selectin"
    )

    def to_json(self):
        return {
            "id": self.id,
            "ingresoMercaderiaId": self.ingresoMercaderiaId,
            "cantidad": float(self.cantidad) if self.cantidad is not None else None,
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("ingresoMercaderiaId", "cantidad"):
            if campo not in data:
                raise KeyError(campo)
        return cls(ingresoMercaderiaId=data["ingresoMercaderiaId"], cantidad=data["cantidad"])

    def update_from_json(self, data):
        if "ingresoMercaderiaId" in data:
            self.ingresoMercaderiaId = data["ingresoMercaderiaId"]
        if "cantidad" in data:
            self.cantidad = data["cantidad"]
