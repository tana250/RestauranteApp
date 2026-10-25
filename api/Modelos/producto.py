from decimal import Decimal
from typing import List

from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Producto(Base):
    __tablename__ = "producto"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    recetas_productos: Mapped[List["RecetaProducto"]] = relationship(
        back_populates="producto", lazy="selectin"
    )

    def to_json(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "valor": float(self.valor) if self.valor is not None else None,
            "activo": bool(self.activo),
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("nombre", "valor"):
            if campo not in data:
                raise KeyError(campo)
        activo = data.get("activo", True)
        if isinstance(activo, str):
            activo = activo.lower() == "true"
        return cls(nombre=data["nombre"], valor=data["valor"], activo=bool(activo))

    def update_from_json(self, data):
        if "nombre" in data:
            self.nombre = data["nombre"]
        if "valor" in data:
            self.valor = data["valor"]
        if "activo" in data:
            activo = data["activo"]
            if isinstance(activo, str):
                activo = activo.lower() == "true"
            self.activo = bool(activo)
