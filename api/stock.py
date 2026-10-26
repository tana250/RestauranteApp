from decimal import Decimal
from unicodedata import combining, normalize

from sqlalchemy import func, select

from .database import db_session
from .Modelos.egreso_mercaderia import EgresoMercaderia
from .Modelos.ingreso_mercaderia import IngresoMercaderia
from .Modelos.unidades_medida import UnidadMedida


# El stock se lleva en una unidad base por familia: gramos, mililitros
# y unidades. Así una receta en kg puede compararse con ingresos en g.
_FACTORES = {
    "kg": ("masa", Decimal("1000")),
    "kilogramo": ("masa", Decimal("1000")),
    "kilogramos": ("masa", Decimal("1000")),
    "g": ("masa", Decimal("1")),
    "gr": ("masa", Decimal("1")),
    "gramo": ("masa", Decimal("1")),
    "gramos": ("masa", Decimal("1")),
    "lt": ("volumen", Decimal("1000")),
    "l": ("volumen", Decimal("1000")),
    "litro": ("volumen", Decimal("1000")),
    "litros": ("volumen", Decimal("1000")),
    "ml": ("volumen", Decimal("1")),
    "mililitro": ("volumen", Decimal("1")),
    "mililitros": ("volumen", Decimal("1")),
    "unidad": ("unidad", Decimal("1")),
    "unidades": ("unidad", Decimal("1")),
    "u": ("unidad", Decimal("1")),
}


def _normalizar_unidad(nombre):
    texto = (nombre or "").strip().lower().rstrip(".")
    return "".join(
        caracter
        for caracter in normalize("NFKD", texto)
        if not combining(caracter)
    )


def _grupo_y_factor(nombre):
    normalizado = _normalizar_unidad(nombre)
    return _FACTORES.get(normalizado, (normalizado, Decimal("1")))


def stock_por_insumo():
    """Devuelve {(insumoId, familia): cantidadBase}."""
    stock = {}

    ingresos = db_session.execute(
        select(
            IngresoMercaderia.insumoId,
            UnidadMedida.nombre,
            func.coalesce(func.sum(IngresoMercaderia.cantidad), 0),
        )
        .join(
            UnidadMedida,
            IngresoMercaderia.unidadMedidaId == UnidadMedida.id,
        )
        .group_by(IngresoMercaderia.insumoId, UnidadMedida.nombre)
    ).all()

    for insumo_id, unidad, cantidad in ingresos:
        grupo, factor = _grupo_y_factor(unidad)
        clave = (insumo_id, grupo)
        stock[clave] = stock.get(clave, Decimal("0")) + Decimal(cantidad) * factor

    egresos = db_session.execute(
        select(
            IngresoMercaderia.insumoId,
            UnidadMedida.nombre,
            func.coalesce(func.sum(EgresoMercaderia.cantidad), 0),
        )
        .join(
            EgresoMercaderia,
            EgresoMercaderia.ingresoMercaderiaId == IngresoMercaderia.id,
        )
        .join(
            UnidadMedida,
            IngresoMercaderia.unidadMedidaId == UnidadMedida.id,
        )
        .group_by(IngresoMercaderia.insumoId, UnidadMedida.nombre)
    ).all()

    for insumo_id, unidad, cantidad in egresos:
        grupo, factor = _grupo_y_factor(unidad)
        clave = (insumo_id, grupo)
        stock[clave] = stock.get(clave, Decimal("0")) - Decimal(cantidad) * factor

    return stock


def stock_disponible(stock, insumo_id, unidad, cantidad):
    """
    Devuelve (cantidad disponible expresada en ``unidad``, suficiente).

    Si la unidad no es convertible, sólo se compara contra ingresos de
    la misma unidad.
    """
    grupo, factor = _grupo_y_factor(unidad)
    base = stock.get((insumo_id, grupo), Decimal("0"))
    requerido = Decimal(cantidad) * factor

    disponible = base / factor if factor else base
    return disponible, base >= requerido
