from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ProductoVenta(Base):
    __tablename__ = "producto_venta"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ventaId: Mapped[int] = mapped_column(ForeignKey("venta.id"), nullable=False)
    productoId: Mapped[int] = mapped_column(ForeignKey("producto.id"), nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    venta: Mapped["Venta"] = relationship(back_populates="producto_ventas", lazy="selectin")
    producto: Mapped["Producto"] = relationship(lazy="selectin")

    def to_json(self):
        return {
            "id": self.id,
            "ventaId": self.ventaId,
            "productoId": self.productoId,
            "precio": float(self.precio) if self.precio is not None else None,
            "cantidad": int(self.cantidad) if self.cantidad is not None else None,
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("ventaId", "productoId", "precio", "cantidad"):
            if campo not in data:
                raise KeyError(campo)
        return cls(
            ventaId=data["ventaId"],
            productoId=data["productoId"],
            precio=data["precio"],
            cantidad=int(data.get("cantidad") or 1),
        )

    def update_from_json(self, data):
        if "ventaId" in data:
            self.ventaId = data["ventaId"]
        if "productoId" in data:
            self.productoId = data["productoId"]
        if "precio" in data:
            self.precio = data["precio"]
        if "cantidad" in data:
            self.cantidad = int(data["cantidad"])
