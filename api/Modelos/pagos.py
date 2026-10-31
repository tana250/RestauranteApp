from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Numeric, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Pago(Base):
    __tablename__ = "pagos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ventaId: Mapped[int] = mapped_column(ForeignKey("venta.id"), nullable=False)
    metodoPagoId: Mapped[int] = mapped_column(ForeignKey("metodos_pago.id"), nullable=False)
    importe: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    hora: Mapped[time] = mapped_column(Time, nullable=False)

    venta: Mapped["Venta"] = relationship(back_populates="pagos", lazy="selectin")
    metodo_pago: Mapped["MetodoPago"] = relationship(back_populates="pagos", lazy="selectin")

    def to_json(self):
        return {
            "id": self.id,
            "ventaId": self.ventaId,
            "metodoPagoId": self.metodoPagoId,
            "importe": float(self.importe) if self.importe is not None else None,
            "fecha": self.fecha.isoformat() if self.fecha is not None else None,
            "hora": self.hora.isoformat() if self.hora is not None else None,
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("ventaId", "metodoPagoId", "importe", "fecha", "hora"):
            if campo not in data:
                raise KeyError(campo)
        fecha = data["fecha"]
        if isinstance(fecha, str):
            fecha = date.fromisoformat(fecha)
        hora = cls._a_time(data["hora"])
        return cls(ventaId=data["ventaId"], metodoPagoId=data["metodoPagoId"], importe=data["importe"], fecha=fecha, hora=hora)

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
        if "hora" in data:
            self.hora = self._a_time(data["hora"])

    @staticmethod
    def _a_time(valor):
        if isinstance(valor, time):
            return valor
        if isinstance(valor, datetime):
            return valor.time()
        if isinstance(valor, date):
            return time(0, 0, 0)
        texto = str(valor).strip()
        if not texto:
            return time(0, 0, 0)
        try:
            return time.fromisoformat(texto)
        except ValueError:
            raise ValueError("hora debe tener formato HH:MM[:SS]")
