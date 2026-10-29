from decimal import Decimal
from typing import List, Optional

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class EgresoMercaderia(Base):
    __tablename__ = "egreso_mercaderia"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ventaId: Mapped[Optional[int]] = mapped_column(ForeignKey("venta.id"), nullable=True)
    ingresoMercaderiaId: Mapped[int] = mapped_column(
        ForeignKey("ingreso_mercaderia.id"), nullable=False
    )
    cantidad: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)

    ingreso_mercaderia: Mapped["IngresoMercaderia"] = relationship(
        lazy="selectin"
    )
    venta: Mapped["Venta"] = relationship(back_populates="egresos", lazy="selectin")
    consumos_personal: Mapped[List["ConsumoPersonal"]] = relationship(
        back_populates="egreso_mercaderia", lazy="selectin"
    )

    def to_json(self):
        return {
            "id": self.id,
            "ventaId": self.ventaId,
            "ingresoMercaderiaId": self.ingresoMercaderiaId,
            "cantidad": float(self.cantidad) if self.cantidad is not None else None,
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("ingresoMercaderiaId", "cantidad", "ventaId"):
            if campo not in data:
                raise KeyError(campo)
        return cls(
            ingresoMercaderiaId=data["ingresoMercaderiaId"],
            cantidad=data["cantidad"],
            ventaId=data.get("ventaId"),
        )

    def update_from_json(self, data):
        if "ventaId" in data:
            self.ventaId = data.get("ventaId")
        if "ingresoMercaderiaId" in data:
            self.ingresoMercaderiaId = data["ingresoMercaderiaId"]
        if "cantidad" in data:
            self.cantidad = data["cantidad"]
