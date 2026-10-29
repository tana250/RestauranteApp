from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ventaId: Mapped[int] = mapped_column(ForeignKey("venta.id"), nullable=False)
    metodoPagoId: Mapped[int] = mapped_column(ForeignKey("metodos_pago.id"), nullable=False)
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)

    venta: Mapped["Venta"] = relationship(back_populates="pagos", lazy="selectin")
    metodo_pago: Mapped["MetodoPago"] = relationship(back_populates="pagos", lazy="selectin")

    def to_json(self):
        return {
            "id": self.id,
            "ventaId": self.ventaId,
            "metodoPagoId": self.metodoPagoId,
            "importe": float(self.importe) if self.importe is not None else None,
            "fecha": self.fecha.isoformat() if self.fecha is not None else None,
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("ventaId", "metodoPagoId", "importe", "fecha"):
            if campo not in data:
                raise KeyError(campo)
        fecha = data["fecha"]
        if isinstance(fecha, str):
            fecha = date.fromisoformat(fecha)
        return cls(ventaId=data["ventaId"], metodoPagoId=data["metodoPagoId"], importe=data["importe"], fecha=fecha)

    def update_from_json(self, data):
        if "ventaId" in data:
            self.ventaId = data["ventaId"]
        if "metodoPagoId" in data:
            self.metodoPagoId = data["metodoPagoId"]
        if "importe" in data:
            self.importe = data["importe"]
        if "fecha" in data:
            fecha = data["fecha"]
            if isinstance(fecha, str):
                fecha = date.fromisoformat(fecha)
            self.fecha = fecha
