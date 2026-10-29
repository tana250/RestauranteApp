from datetime import date
from decimal import Decimal, InvalidOperation

from flask import jsonify
from flask.views import MethodView
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from ..database import db_session
from ..Modelos.metodos_pago import MetodoPago
from ..Modelos.pagos import Pago
from ..Modelos.venta import Venta
from .crudGenerico import datos_json, respuesta_error, register_api


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


class PagosVentaAPI(MethodView):
    """Registra un pago sobre una venta y consulta su estado."""

    init_every_request = False

    def post(self):
        data = datos_json()

        try:
            venta_id = _entero(data.get("ventaId"), "ventaId")
            metodo_pago_id = _entero(data.get("metodoPagoId"), "metodoPagoId")
            importe = _decimal(data.get("importe"), "importe", positivo=True)
            fecha_pago = _fecha(data.get("fecha"))

            venta = db_session.get(Venta, venta_id)
            if venta is None:
                return jsonify({"error": "Venta no encontrada"}), 404

            metodo_pago = db_session.get(MetodoPago, metodo_pago_id)
            if metodo_pago is None:
                return jsonify({"error": "Metodo de pago no encontrado"}), 404

            pago = Pago(
                ventaId=venta_id,
                metodoPagoId=metodo_pago_id,
                importe=importe,
                fecha=fecha_pago,
            )
            db_session.add(pago)
            db_session.commit()

            return jsonify(pago.to_json()), 201
        except (KeyError, ValueError, SQLAlchemyError) as exc:
            return respuesta_error(exc)

    def get(self, ventaId):
        venta = db_session.get(Venta, ventaId)
        if venta is None:
            return jsonify({"error": "Venta no encontrada"}), 404

        pagos = db_session.scalars(
            select(Pago).where(Pago.ventaId == ventaId).order_by(Pago.id)
        ).all()

        total = Decimal("0")
        for producto_venta in venta.producto_ventas:
            total += (producto_venta.precio or Decimal("0")) * (producto_venta.cantidad or 0)

        pagado = sum((pago.importe or Decimal("0") for pago in pagos), Decimal("0"))

        if pagado >= total:
            estado = "completo"
        elif pagado > 0:
            estado = "parcial"
        else:
            estado = "sin_pago"

        return jsonify(
            {
                "venta": venta.to_json(),
                "pagos": [pago.to_json() for pago in pagos],
                "total": float(total),
                "pagado": float(pagado),
                "estado": estado,
            }
        )


def register_pagos(app):
    register_api(app, Pago, "pagos")

    app.add_url_rule(
        "/pagos/guardar",
        view_func=PagosVentaAPI.as_view("pagos-guardar"),
        methods=["POST"],
    )

    app.add_url_rule(
        "/pagos/venta/<int:ventaId>",
        view_func=PagosVentaAPI.as_view("pagos-venta"),
        methods=["GET"],
    )
