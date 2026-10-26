from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Insumo(Base):
    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tipoInsumoId: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tipos_insumo.id"), nullable=True
    )
    marcaId: Mapped[Optional[int]] = mapped_column(
        ForeignKey("marcas.id"), nullable=True
    )

    tipo_insumo: Mapped["TipoInsumo"] = relationship(
        back_populates="insumos", lazy="selectin"
    )
    marca: Mapped["Marca"] = relationship(back_populates="insumos", lazy="selectin")
    ingresos_mercaderia: Mapped[List["IngresoMercaderia"]] = relationship(
        back_populates="insumo", lazy="selectin"
    )
    recetas_productos: Mapped[List["RecetaProducto"]] = relationship(
        back_populates="insumo", lazy="selectin"
    )

    def to_json(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipoInsumoId": self.tipoInsumoId,
            "marcaId": self.marcaId,
            "tipoInsumoNombre": self.tipo_insumo.tipo if self.tipo_insumo else None,
            "marcaNombre": self.marca.nombre if self.marca else None,
        }

    @classmethod
    def from_json(cls, data):
        if "nombre" not in data:
            raise KeyError("nombre")
        return cls(
            nombre=data["nombre"],
            tipoInsumoId=data.get("tipoInsumoId"),
            marcaId=data.get("marcaId"),
        )

    def update_from_json(self, data):
        if "nombre" in data:
            self.nombre = data["nombre"]
        if "tipoInsumoId" in data:
            self.tipoInsumoId = data["tipoInsumoId"]
        if "marcaId" in data:
            self.marcaId = data["marcaId"]
