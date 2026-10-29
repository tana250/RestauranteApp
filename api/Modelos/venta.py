from datetime import date, datetime
from decimal import Decimal
from typing import List

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Venta(Base):
    __tablename__ = "venta"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    mozoId: Mapped[int] = mapped_column(ForeignKey("mozo.id"), nullable=False)
    mesaId: Mapped[int] = mapped_column(ForeignKey("mesa.id"), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    mozo: Mapped["Mozo"] = relationship(back_populates="ventas", lazy="selectin")
    mesa: Mapped["Mesa"] = relationship(back_populates="ventas", lazy="selectin")
    producto_ventas: Mapped[List["ProductoVenta"]] = relationship(
        back_populates="venta", lazy="selectin"
    )
    pagos: Mapped[List["Pago"]] = relationship(back_populates="venta", lazy="selectin")
    egresos: Mapped[List["EgresoMercaderia"]] = relationship(
        back_populates="venta", lazy="selectin"
    )

    def to_json(self):
        total = Decimal("0")
        for producto_venta in self.producto_ventas:
            total += (producto_venta.precio or Decimal("0")) * (
                producto_venta.cantidad or 0
            )

        pagado = sum(
            (pago.importe or Decimal("0") for pago in self.pagos), Decimal("0")
        )

        if pagado >= total:
            estado = "completo"
        elif pagado > 0:
            estado = "parcial"
        else:
            estado = "sin_pago"

        return {
            "id": self.id,
            "mozoId": self.mozoId,
            "mesaId": self.mesaId,
            "fecha": self.fecha.isoformat() if self.fecha is not None else None,
            "productos": [
                {
                    "id": producto_venta.id,
                    "productoId": producto_venta.productoId,
                    "precio": float(producto_venta.precio)
                    if producto_venta.precio is not None
                    else None,
                    "cantidad": int(producto_venta.cantidad)
                    if producto_venta.cantidad is not None
                    else None,
                }
                for producto_venta in self.producto_ventas
            ],
            "pagos": [
                {
                    "id": pago.id,
                    "ventaId": pago.ventaId,
                    "metodoPagoId": pago.metodoPagoId,
                    "importe": float(pago.importe) if pago.importe is not None else None,
                    "fecha": pago.fecha.isoformat() if pago.fecha is not None else None,
                }
                for pago in self.pagos
            ],
            "total": float(total),
            "pagado": float(pagado),
            "estado": estado,
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("mozoId", "mesaId", "fecha"):
            if campo not in data:
                raise KeyError(campo)
        fecha = cls._a_datetime(data["fecha"])
        return cls(mozoId=data["mozoId"], mesaId=data["mesaId"], fecha=fecha)

    def update_from_json(self, data):
        if "mozoId" in data:
            self.mozoId = data["mozoId"]
        if "mesaId" in data:
            self.mesaId = data["mesaId"]
        if "fecha" in data:
            self.fecha = self._a_datetime(data["fecha"])

    @staticmethod
    def _a_datetime(valor):
        if isinstance(valor, datetime):
            return valor
        if isinstance(valor, date):
            return datetime.combine(valor, datetime.min.time())
        return datetime.combine(date.fromisoformat(str(valor)), datetime.min.time())
