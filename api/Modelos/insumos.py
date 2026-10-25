from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Insumo(Base):
    __tablename__ = "insumos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tipoInsumoId: Mapped[int] = mapped_column(
        ForeignKey("tipos_insumo.id"), nullable=False
    )
    marcaId: Mapped[int] = mapped_column(ForeignKey("marcas.id"), nullable=False)

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
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("nombre", "tipoInsumoId", "marcaId"):
            if campo not in data:
                raise KeyError(campo)
        return cls(
            nombre=data["nombre"],
            tipoInsumoId=data["tipoInsumoId"],
            marcaId=data["marcaId"],
        )

    def update_from_json(self, data):
        if "nombre" in data:
            self.nombre = data["nombre"]
        if "tipoInsumoId" in data:
            self.tipoInsumoId = data["tipoInsumoId"]
        if "marcaId" in data:
            self.marcaId = data["marcaId"]
