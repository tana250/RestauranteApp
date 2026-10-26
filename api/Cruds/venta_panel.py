from datetime import date
from decimal import Decimal, InvalidOperation

from flask import jsonify
from flask.views import MethodView
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from ..database import db_session
from ..Modelos.egreso_mercaderia import EgresoMercaderia
from ..Modelos.ingreso_mercaderia import IngresoMercaderia
from ..Modelos.mesa import Mesa
from ..Modelos.mozo import Mozo
from ..Modelos.producto import Producto
from ..Modelos.producto_venta import ProductoVenta
from ..Modelos.receta_producto import RecetaProducto
from ..Modelos.venta import Venta
from ..stock import stock_disponible, stock_por_insumo
from .crudGenerico import datos_json, respuesta_error


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


def _resolver_mesa(data):
    mesa = db_session.get(Mesa, _entero(data.get("mesaId"), "mesaId"))
    if mesa is None:
        raise ValueError("Mesa no existe")
    return mesa


def _resolver_mozo(data):
    mozo = db_session.get(Mozo, _entero(data.get("mozoId"), "mozoId"))
    if mozo is None:
        raise ValueError("Mozo no existe")
    return mozo


def _resolver_producto(data):
    producto = db_session.get(Producto, _entero(data.get("productoId"), "productoId"))
    if producto is None:
        raise ValueError("Producto no existe")

    if not producto.activo:
        raise ValueError(f"El producto {producto.nombre} está inactivo")

    cantidad_valor = data.get("cantidad")
    if cantidad_valor in (None, ""):
        cantidad_valor = Decimal("1")

    cantidad = _decimal(cantidad_valor, "cantidad", positivo=True)
    precio_valor = data.get("precio")
    if precio_valor in (None, ""):
        precio_valor = producto.valor

    precio = _decimal(precio_valor, "precio", positivo=False)

    return producto, cantidad, precio


def _ingreso_disponible(insumo_id, unidad_nombre, cantidad):
    stock = stock_por_insumo()
    disponible, suficiente = stock_disponible(
        stock,
        insumo_id,
        unidad_nombre,
        cantidad,
    )

    if not suficiente:
        raise ValueError("Stock insuficiente para la venta")

    ingresos = db_session.scalars(
        select(IngresoMercaderia)
        .where(IngresoMercaderia.insumoId == insumo_id)
        .order_by(IngresoMercaderia.id)
    ).all()

    from ..stock import _grupo_y_factor

    grupo, factor = _grupo_y_factor(unidad_nombre)

    for ingreso in ingresos:
        egresos = db_session.scalars(
            select(EgresoMercaderia).where(
                EgresoMercaderia.ingresoMercaderiaId == ingreso.id
            )
        ).all()
        egresado = sum(
            (egreso.cantidad or Decimal("0")) for egreso in egresos
        )
        restante_base = ingreso.cantidad - egresado
        restante = restante_base / factor if factor else restante_base

        if restante >= cantidad:
            return ingreso

    raise ValueError("No hay stock disponible para el ingreso")


def _respuesta_venta(venta):
    return {
        "id": venta.id,
        "mozoId": venta.mozoId,
        "mesaId": venta.mesaId,
        "fecha": venta.fecha.isoformat() if venta.fecha is not None else None,
        "productos": [
            {
                "id": producto_venta.id,
                "ventaId": producto_venta.ventaId,
                "productoId": producto_venta.productoId,
                "precio": float(producto_venta.precio)
                if producto_venta.precio is not None
                else None,
                "egresoMercaderiaId": producto_venta.egresoMercaderiaId,
            }
            for producto_venta in venta.producto_ventas
        ],
    }


class VentaGuardarAPI(MethodView):
    """Crea una venta con sus productoVentas y el egreso calculado."""

    init_every_request = False

    def post(self):
        data = datos_json()

        try:
            mesa = _resolver_mesa(data)
            mozo = _resolver_mozo(data)
            fecha = _fecha(data.get("fecha"))
            producto_lines = data.get("productos")

            if not isinstance(producto_lines, list) or not producto_lines:
                raise ValueError("productos debe ser una lista no vacía")

            venta = Venta(
                mozoId=mozo.id,
                mesaId=mesa.id,
                fecha=fecha,
            )
            db_session.add(venta)
            db_session.flush()

            for linea in producto_lines:
                if not isinstance(linea, dict):
                    raise ValueError("Cada producto de la venta debe ser un objeto")

                producto, cantidad, precio = _resolver_producto(linea)
                recetas = db_session.scalars(
                    select(RecetaProducto).where(
                        RecetaProducto.productoId == producto.id
                    )
                ).all()

                if not recetas:
                    raise ValueError(f"El producto {producto.nombre} no tiene receta")

                receta = recetas[0]
                insumo = receta.insumo
                unidad = receta.unidad_medida
                unidad_nombre = unidad.nombre if unidad is not None else ""

                required = receta.cantidad * cantidad
                ingreso = _ingreso_disponible(
                    receta.insumoId,
                    unidad_nombre,
                    required,
                )

                egreso = EgresoMercaderia(
                    ingresoMercaderiaId=ingreso.id,
                    cantidad=required,
                )
                db_session.add(egreso)
                db_session.flush()

                producto_venta = ProductoVenta(
                    ventaId=venta.id,
                    productoId=producto.id,
                    precio=precio,
                    egresoMercaderiaId=egreso.id,
                )
                db_session.add(producto_venta)

            db_session.commit()
        except (KeyError, ValueError, SQLAlchemyError) as exc:
            return respuesta_error(exc)

        return jsonify(_respuesta_venta(venta)), 201


class VentaDetalleAPI(MethodView):
    init_every_request = False

    def get(self, id):
        venta = db_session.get(Venta, id)
        if venta is None:
            return jsonify({"error": "No encontrado"}), 404
        return jsonify(_respuesta_venta(venta))


def register_venta_panel(app):
    app.add_url_rule(
        "/venta/guardar",
        view_func=VentaGuardarAPI.as_view("venta-guardar"),
        methods=["POST"],
    )
    app.add_url_rule(
        "/venta/<int:id>/detalle",
        view_func=VentaDetalleAPI.as_view("venta-detalle"),
        methods=["GET"],
    )
