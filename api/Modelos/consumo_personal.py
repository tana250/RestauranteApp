from datetime import date, datetime, time

from sqlalchemy import DateTime, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ConsumoPersonal(Base):
    __tablename__ = "consumo_personal"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    personalId: Mapped[int] = mapped_column(ForeignKey("personal.id"), nullable=False)
    egresoMercaderiaId: Mapped[int] = mapped_column(
        ForeignKey("egreso_mercaderia.id"), nullable=False
    )
    fecha: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    hora: Mapped[time] = mapped_column(Time, nullable=False)

    personal: Mapped["Personal"] = relationship(
        back_populates="consumos_personal", lazy="selectin"
    )
    egreso_mercaderia: Mapped["EgresoMercaderia"] = relationship(
        back_populates="consumos_personal", lazy="selectin"
    )

    def to_json(self):
        return {
            "id": self.id,
            "personalId": self.personalId,
            "egresoMercaderiaId": self.egresoMercaderiaId,
            "fecha": self.fecha.isoformat() if self.fecha is not None else None,
            "hora": self.hora.isoformat() if self.hora is not None else None,
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("personalId", "egresoMercaderiaId", "fecha", "hora"):
            if campo not in data:
                raise KeyError(campo)
        fecha = cls._a_datetime(data["fecha"])
        hora = cls._a_time(data["hora"])
        return cls(
            personalId=data["personalId"],
            egresoMercaderiaId=data["egresoMercaderiaId"],
            fecha=fecha,
            hora=hora,
        )

    def update_from_json(self, data):
        if "personalId" in data:
            self.personalId = data["personalId"]
        if "egresoMercaderiaId" in data:
            self.egresoMercaderiaId = data["egresoMercaderiaId"]
        if "fecha" in data:
            self.fecha = cls._a_datetime(data["fecha"])
        if "hora" in data:
            self.hora = cls._a_time(data["hora"])

    @staticmethod
    def _a_datetime(valor):
        if isinstance(valor, datetime):
            return valor
        if isinstance(valor, date):
            return datetime.combine(valor, time.min)
        return datetime.combine(date.fromisoformat(str(valor)), time.min)

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
