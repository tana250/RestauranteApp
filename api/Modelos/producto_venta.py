from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ProductoVenta(Base):
    __tablename__ = "productoVenta"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ventaId: Mapped[int] = mapped_column(ForeignKey("venta.id"), nullable=False)
    productoId: Mapped[int] = mapped_column(ForeignKey("producto.id"), nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    egresoMercaderiaId: Mapped[int] = mapped_column(
        ForeignKey("egreso_mercaderia.id"), nullable=False
    )

    venta: Mapped["Venta"] = relationship(back_populates="producto_ventas", lazy="selectin")
    producto: Mapped["Producto"] = relationship(lazy="selectin")
    egreso_mercaderia: Mapped["EgresoMercaderia"] = relationship(
        back_populates="producto_ventas", lazy="selectin"
    )

    def to_json(self):
        return {
            "id": self.id,
            "ventaId": self.ventaId,
            "productoId": self.productoId,
            "precio": float(self.precio) if self.precio is not None else None,
            "egresoMercaderiaId": self.egresoMercaderiaId,
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("ventaId", "productoId", "precio", "egresoMercaderiaId"):
            if campo not in data:
                raise KeyError(campo)
        return cls(
            ventaId=data["ventaId"],
            productoId=data["productoId"],
            precio=data["precio"],
            egresoMercaderiaId=data["egresoMercaderiaId"],
        )

    def update_from_json(self, data):
        if "ventaId" in data:
            self.ventaId = data["ventaId"]
        if "productoId" in data:
            self.productoId = data["productoId"]
        if "precio" in data:
            self.precio = data["precio"]
        if "egresoMercaderiaId" in data:
            self.egresoMercaderiaId = data["egresoMercaderiaId"]
