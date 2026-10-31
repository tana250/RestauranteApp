from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation

from flask import jsonify
from flask.views import MethodView
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from ..database import db_session
from ..Modelos.consumo_personal import ConsumoPersonal
from ..Modelos.egreso_mercaderia import EgresoMercaderia
from ..Modelos.ingreso_mercaderia import IngresoMercaderia
from ..Modelos.insumos import Insumo
from ..Modelos.personal import Personal
from ..Modelos.unidades_medida import UnidadMedida
from ..stock import ingreso_con_stock_suficiente
from .crudGenerico import datos_json, respuesta_error


def _texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} es obligatorio")
    return valor.strip()


def _entero(valor, campo):
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{campo} debe ser un entero")


def _decimal(valor, campo, positivo=False):
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"{campo} debe ser numérico")

    if not numero.is_finite():
        raise ValueError(f"{campo} debe ser numérico")

    if positivo and numero <= 0:
        raise ValueError(f"{campo} debe ser mayor a 0")

    if not positivo and numero < 0:
        raise ValueError(f"{campo} no puede ser negativo")

    return numero


def _fecha(valor):
    if valor in (None, ""):
        return datetime.now()

    if isinstance(valor, datetime):
        return valor

    if isinstance(valor, date):
        return datetime.combine(valor, time.min)

    try:
        return datetime.combine(date.fromisoformat(str(valor)), time.min)
    except ValueError:
        raise ValueError("fecha debe tener formato AAAA-MM-DD")


def _hora(valor):
    if valor in (None, ""):
        return datetime.now().time()

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


def _resolver_insumo(data):
    insumo_id = data.get("insumoId")

    if insumo_id in (None, ""):
        nombre = _texto(data.get("insumoNombre") or data.get("insumo"), "insumo")
        insumo = db_session.scalar(
            select(Insumo)
            .where(func.lower(Insumo.nombre) == nombre.lower())
            .order_by(Insumo.id)
        )
        if insumo is None:
            raise ValueError("El insumo seleccionado no existe")
        return insumo

    insumo = db_session.get(Insumo, _entero(insumo_id, "insumoId"))
    if insumo is None:
        raise ValueError("El insumo seleccionado no existe")
    return insumo


def _resolver_ingreso(data):
    """
    Devuelve el ingreso de mercadería sobre el que se va a egresar stock.

    Acepta ``ingresoMercaderiaId`` (para egresos ya registrados) o
    ``insumoId``/`insumoNombre` + ``unidadMedidaId`` (para consumos nuevos).
    """
    cantidad = _decimal(data.get("cantidad"), "cantidad", positivo=True)

    ingreso_id = data.get("ingresoMercaderiaId")

    if ingreso_id in (None, ""):
        insumo = _resolver_insumo(data)
        unidad_id = data.get("unidadMedidaId")
        unidad_nombre = None
        if unidad_id not in (None, ""):
            unidad = db_session.get(
                UnidadMedida,
                _entero(unidad_id, "unidadMedidaId"),
            )
            if unidad is None:
                raise ValueError("La unidad de medida seleccionada no existe")
            unidad_nombre = unidad.nombre
        return ingreso_con_stock_suficiente(
            insumo.id,
            unidad_nombre,
            cantidad,
            mensaje="Stock insuficiente para el consumo personal",
        )

    ingreso = db_session.get(IngresoMercaderia, _entero(ingreso_id, "ingresoMercaderiaId"))
    if ingreso is None:
        raise ValueError("El ingreso de mercadería no existe")

    unidad_nombre = ingreso.unidad_medida.nombre if ingreso.unidad_medida else None
    ingreso_con_stock_suficiente(
        ingreso.insumoId,
        unidad_nombre,
        cantidad,
        mensaje="Stock insuficiente para el consumo personal",
    )

    return ingreso


def _respuesta_consumo(consumo):
    return {
        "id": consumo.id,
        "personalId": consumo.personalId,
        "egresoMercaderiaId": consumo.egresoMercaderiaId,
        "fecha": consumo.fecha.isoformat() if consumo.fecha is not None else None,
        "hora": consumo.hora.isoformat() if consumo.hora is not None else None,
    }


class ConsumoPersonalGuardarAPI(MethodView):
    """
    Registra un consumo de personal: crea el/los egreso(s) de
    mercadería (ventaId NULL = consumo personal) y el consumo en una
    sola transacción. Ante cualquier error se hace rollback.
    """

    init_every_request = False

    def post(self):
        data = datos_json()

        try:
            personal_id = _entero(data.get("personalId") or data.get("personal_id"), "personalId")
            personal = db_session.get(Personal, personal_id)
            if personal is None:
                raise ValueError("El personal seleccionado no existe")

            fecha = _fecha(data.get("fecha"))
            hora = _hora(data.get("hora"))
            fecha = datetime.combine(fecha.date(), hora)

            egresos = data.get("egresos")
            if not isinstance(egresos, list) or not egresos:
                raise ValueError("egresos debe ser una lista no vacía")

            consumos = []
            for linea in egresos:
                if not isinstance(linea, dict):
                    raise ValueError("Cada consumo debe ser un objeto")

                ingreso = _resolver_ingreso(linea)
                cantidad = _decimal(linea.get("cantidad"), "cantidad", positivo=True)

                egreso = EgresoMercaderia(
                    ventaId=None,
                    ingresoMercaderiaId=ingreso.id,
                    cantidad=cantidad,
                )
                db_session.add(egreso)
                db_session.flush()

                consumo = ConsumoPersonal(
                    personalId=personal.id,
                    egresoMercaderiaId=egreso.id,
                    fecha=fecha,
                    hora=hora,
                )
                db_session.add(consumo)
                consumos.append(consumo)

            db_session.commit()

            return jsonify([_respuesta_consumo(consumo) for consumo in consumos]), 201
        except (KeyError, ValueError, SQLAlchemyError) as exc:
            return respuesta_error(exc)


def register_consumo_personal_panel(app):
    app.add_url_rule(
        "/consumoPersonal/guardar",
        view_func=ConsumoPersonalGuardarAPI.as_view(
            "consumo-personal-guardar"
        ),
        methods=["POST"],
    )
