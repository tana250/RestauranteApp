from datetime import date

from sqlalchemy import Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ConsumoPersonal(Base):
    __tablename__ = "consumoPersonal"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    personalId: Mapped[int] = mapped_column(ForeignKey("personal.id"), nullable=False)
    egresoMercaderiaId: Mapped[int] = mapped_column(
        ForeignKey("egreso_mercaderia.id"), nullable=False
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)

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
        }

    @classmethod
    def from_json(cls, data):
        for campo in ("personalId", "egresoMercaderiaId", "fecha"):
            if campo not in data:
                raise KeyError(campo)
        fecha = data["fecha"]
        if isinstance(fecha, str):
            fecha = date.fromisoformat(fecha)
        return cls(personalId=data["personalId"], egresoMercaderiaId=data["egresoMercaderiaId"], fecha=fecha)

    def update_from_json(self, data):
        if "personalId" in data:
            self.personalId = data["personalId"]
        if "egresoMercaderiaId" in data:
            self.egresoMercaderiaId = data["egresoMercaderiaId"]
        if "fecha" in data:
            fecha = data["fecha"]
            if isinstance(fecha, str):
                fecha = date.fromisoformat(fecha)
            self.fecha = fecha
