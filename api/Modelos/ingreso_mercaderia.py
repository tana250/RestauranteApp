from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class IngresoMercaderia(Base):
    __tablename__ = "ingreso_mercaderia"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    proveedorId: Mapped[int] = mapped_column(
        ForeignKey("proveedor.id"), nullable=False
    )
    insumoId: Mapped[int] = mapped_column(ForeignKey("insumos.id"), nullable=False)
    unidadMedidaId: Mapped[int] = mapped_column(
        ForeignKey("unidades_medida.id"), nullable=False
    )
    cantidad: Mapped[Decimal] = mapped_column(Numeric(10, 3), nullable=False)
    precioUnitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    proveedor: Mapped["Proveedor"] = relationship(
        back_populates="ingresos_mercaderia", lazy="selectin"
    )
    insumo: Mapped["Insumo"] = relationship(
        back_populates="ingresos_mercaderia", lazy="selectin"
    )
    unidad_medida: Mapped["UnidadMedida"] = relationship(
        back_populates="ingresos_mercaderia", lazy="selectin"
    )

    def to_json(self):
        return {
            "id": self.id,
            "proveedorId": self.proveedorId,
            "insumoId": self.insumoId,
            "unidadMedidaId": self.unidadMedidaId,
            "cantidad": float(self.cantidad) if self.cantidad is not None else None,
            "precioUnitario": float(self.precioUnitario)
            if self.precioUnitario is not None
            else None,
            "fecha": self.fecha.isoformat() if self.fecha is not None else None,
            "proveedorNombre": self.proveedor.nombre if self.proveedor else None,
            "insumoNombre": self.insumo.nombre if self.insumo else None,
            "unidadMedida": self.unidad_medida.nombre if self.unidad_medida else None,
        }

    @classmethod
    def from_json(cls, data):
        for campo in (
            "proveedorId",
            "insumoId",
            "unidadMedidaId",
            "cantidad",
            "precioUnitario",
            "fecha",
        ):
            if campo not in data:
                raise KeyError(campo)

        fecha = IngresoMercaderia._a_datetime(data["fecha"])

        return cls(
            proveedorId=data["proveedorId"],
            insumoId=data["insumoId"],
            unidadMedidaId=data["unidadMedidaId"],
            cantidad=data["cantidad"],
            precioUnitario=data["precioUnitario"],
            fecha=fecha,
        )

    def update_from_json(self, data):
        if "proveedorId" in data:
            self.proveedorId = data["proveedorId"]
        if "insumoId" in data:
            self.insumoId = data["insumoId"]
        if "unidadMedidaId" in data:
            self.unidadMedidaId = data["unidadMedidaId"]
        if "cantidad" in data:
            self.cantidad = data["cantidad"]
        if "precioUnitario" in data:
            self.precioUnitario = data["precioUnitario"]
        if "fecha" in data:
            self.fecha = IngresoMercaderia._a_datetime(data["fecha"])

    @staticmethod
    def _a_datetime(valor):
        if isinstance(valor, datetime):
            return valor
        if isinstance(valor, date):
            return datetime.combine(valor, time.min)
        return datetime.combine(date.fromisoformat(str(valor)), time.min)
