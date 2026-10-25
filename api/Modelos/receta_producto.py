from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class RecetaProducto(Base):
    __tablename__ = "recetas_productos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    productoId: Mapped[int] = mapped_column(ForeignKey("producto.id"), nullable=False)
    insumoId: Mapped[int] = mapped_column(ForeignKey("insumos.id"), nullable=False)
    cantidad: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    unidadMedidaId: Mapped[int] = mapped_column(
        ForeignKey("unidades_medida.id"), nullable=False
    )

    producto: Mapped["Producto"] = relationship(
        back_populates="recetas_productos", lazy="selectin"
    )
    insumo: Mapped["Insumo"] = relationship(
        back_populates="recetas_productos", lazy="selectin"
    )
    unidad_medida: Mapped["UnidadMedida"] = relationship(
        back_populates="recetas_productos", lazy="selectin"
    )

    def to_json(self):
        return {
            "id": self.id,
            "productoId": self.productoId,
            "insumoId": self.insumoId,
            "cantidad": float(self.cantidad) if self.cantidad is not None else None,
            "unidadMedidaId": self.unidadMedidaId,
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("productoId", "insumoId", "cantidad", "unidadMedidaId"):
            if campo not in data:
                raise KeyError(campo)
        return cls(
            productoId=data["productoId"],
            insumoId=data["insumoId"],
            cantidad=data["cantidad"],
            unidadMedidaId=data["unidadMedidaId"],
        )

    def update_from_json(self, data):
        if "productoId" in data:
            self.productoId = data["productoId"]
        if "insumoId" in data:
            self.insumoId = data["insumoId"]
        if "cantidad" in data:
            self.cantidad = data["cantidad"]
        if "unidadMedidaId" in data:
            self.unidadMedidaId = data["unidadMedidaId"]
