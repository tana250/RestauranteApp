from datetime import date
from decimal import Decimal, InvalidOperation

from flask import jsonify
from flask.views import MethodView
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError

from ..database import db_session
from ..Modelos.ingreso_mercaderia import IngresoMercaderia
from ..Modelos.insumos import Insumo
from ..Modelos.proveedor import Proveedor
from ..Modelos.unidades_medida import UnidadMedida
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
        return date.today()

    if isinstance(valor, date):
        return valor

    try:
        return date.fromisoformat(str(valor))
    except ValueError:
        raise ValueError("fecha debe tener formato AAAA-MM-DD")


def _resolver_proveedor(data):
    proveedor_id = data.get("proveedorId")

    if proveedor_id not in (None, ""):
        proveedor = db_session.get(Proveedor, _entero(proveedor_id, "proveedorId"))
        if proveedor is None:
            raise ValueError("El proveedor seleccionado no existe")
        return proveedor

    nombre = _texto(
        data.get("proveedorNombre") or data.get("proveedor"),
        "proveedor",
    )
    proveedor = db_session.scalar(
        select(Proveedor)
        .where(func.lower(Proveedor.nombre) == nombre.lower())
        .order_by(Proveedor.id)
    )

    if proveedor is not None:
        return proveedor

    proveedor = Proveedor(nombre=nombre)
    db_session.add(proveedor)
    db_session.flush()
    return proveedor


def _resolver_insumo(data):
    insumo_id = data.get("insumoId")

    if insumo_id not in (None, ""):
        insumo = db_session.get(Insumo, _entero(insumo_id, "insumoId"))
        if insumo is None:
            raise ValueError("El insumo seleccionado no existe")
        return insumo

    nombre = _texto(data.get("insumoNombre") or data.get("insumo"), "insumo")
    insumo = db_session.scalar(
        select(Insumo)
        .where(func.lower(Insumo.nombre) == nombre.lower())
        .order_by(Insumo.id)
    )

    if insumo is not None:
        return insumo

    # Se crea sin marca ni tipo: se completan desde el apartado Insumos.
    insumo = Insumo(nombre=nombre, tipoInsumoId=None, marcaId=None)
    db_session.add(insumo)
    db_session.flush()
    return insumo


def _resolver_unidad(data):
    unidad_id = data.get("unidadMedidaId")
    if unidad_id in (None, ""):
        raise ValueError("La unidad de medida es obligatoria")

    unidad = db_session.get(
        UnidadMedida,
        _entero(unidad_id, "unidadMedidaId"),
    )
    if unidad is None:
        raise ValueError("La unidad de medida seleccionada no existe")
    return unidad


def _respuesta_ingreso(ingreso):
    return {
        "id": ingreso.id,
        "proveedorId": ingreso.proveedorId,
        "proveedorNombre": ingreso.proveedor.nombre,
        "insumoId": ingreso.insumoId,
        "insumoNombre": ingreso.insumo.nombre,
        "unidadMedidaId": ingreso.unidadMedidaId,
        "unidadMedida": ingreso.unidad_medida.nombre,
        "cantidad": float(ingreso.cantidad),
        "precioUnitario": float(ingreso.precioUnitario),
        "fecha": ingreso.fecha.isoformat(),
    }


class IngresoMercaderiaGuardarAPI(MethodView):
    """Crea proveedor/insumo faltantes y el ingreso en una transacción."""

    init_every_request = False

    def post(self):
        data = datos_json()

        try:
            proveedor = _resolver_proveedor(data)
            insumo = _resolver_insumo(data)
            unidad = _resolver_unidad(data)
            cantidad = _decimal(
                data.get("cantidad"),
                "cantidad",
                positivo=True,
            )
            precio = _decimal(
                data.get("precioUnitario", data.get("precio")),
                "precioUnitario",
            )
            fecha = _fecha(data.get("fecha"))

            ingreso = IngresoMercaderia(
                proveedorId=proveedor.id,
                insumoId=insumo.id,
                unidadMedidaId=unidad.id,
                cantidad=cantidad,
                precioUnitario=precio,
                fecha=fecha,
            )
            db_session.add(ingreso)
            db_session.commit()
        except (KeyError, ValueError, SQLAlchemyError) as exc:
            return respuesta_error(exc)

        return jsonify(_respuesta_ingreso(ingreso)), 201


def register_ingreso_mercaderia_panel(app):
    app.add_url_rule(
        "/ingresoMercaderia/guardar",
        view_func=IngresoMercaderiaGuardarAPI.as_view(
            "ingreso-mercaderia-guardar"
        ),
        methods=["POST"],
    )
