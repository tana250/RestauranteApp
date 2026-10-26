from decimal import Decimal, InvalidOperation

from flask import jsonify
from flask.views import MethodView
from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError

from ..database import db_session
from ..Modelos.insumos import Insumo
from ..Modelos.producto import Producto
from ..Modelos.receta_producto import RecetaProducto
from ..Modelos.unidades_medida import UnidadMedida
from ..stock import stock_disponible, stock_por_insumo
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


def _booleano(valor):
    if isinstance(valor, str):
        return valor.strip().lower() in ("true", "1", "si", "sí")
    return bool(valor)


def _normalizar(nombre):
    return (nombre or "").strip().lower()


def _producto_detalle(producto):
    stock = stock_por_insumo()
    insumos = []

    for receta in sorted(producto.recetas_productos, key=lambda item: item.id or 0):
        unidad = receta.unidad_medida.nombre if receta.unidad_medida else ""
        cantidad = receta.cantidad or Decimal("0")
        disponible, suficiente = stock_disponible(
            stock,
            receta.insumoId,
            unidad,
            cantidad,
        )

        insumos.append(
            {
                "id": receta.id,
                "insumoId": receta.insumoId,
                "insumoNombre": receta.insumo.nombre if receta.insumo else None,
                "cantidad": float(cantidad),
                "unidadMedidaId": receta.unidadMedidaId,
                "unidadMedida": unidad,
                "stock": round(float(disponible), 3),
                "suficiente": suficiente,
            }
        )

    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "valor": float(producto.valor) if producto.valor is not None else None,
        "activo": bool(producto.activo),
        "insumos": insumos,
    }


def _resolver_producto(data):
    producto_id = data.get("id")

    if producto_id not in (None, ""):
        producto = db_session.get(Producto, _entero(producto_id, "id"))
        if producto is None:
            raise LookupError("Producto no encontrado")
        return producto, False

    nombre = _texto(data.get("nombre"), "nombre")
    producto = db_session.scalar(
        select(Producto)
        .where(func.lower(Producto.nombre) == nombre.lower())
        .order_by(Producto.id)
    )

    if producto is not None:
        return producto, False

    producto = Producto(nombre=nombre, valor=Decimal("0"), activo=True)
    db_session.add(producto)
    db_session.flush()
    return producto, True


def _resolver_insumo(data):
    insumo_id = data.get("insumoId")

    if insumo_id not in (None, ""):
        insumo = db_session.get(Insumo, _entero(insumo_id, "insumoId"))
        if insumo is None:
            raise ValueError("El insumo seleccionado no existe")
        return insumo

    nombre = _texto(data.get("nombre"), "nombre del insumo")
    insumo = db_session.scalar(
        select(Insumo)
        .where(func.lower(Insumo.nombre) == nombre.lower())
        .order_by(Insumo.id)
    )

    if insumo is not None:
        return insumo

    # Se crea sin marca ni tipo: se completan luego desde el panel de insumos.
    insumo = Insumo(nombre=nombre, tipoInsumoId=None, marcaId=None)
    db_session.add(insumo)
    db_session.flush()
    return insumo


def _resolver_unidad(data):
    unidad_id = data.get("unidadMedidaId")
    if unidad_id in (None, ""):
        raise ValueError("La unidad de medida es obligatoria")

    unidad = db_session.get(UnidadMedida, _entero(unidad_id, "unidadMedidaId"))
    if unidad is None:
        raise ValueError("La unidad de medida seleccionada no existe")
    return unidad


class ProductoGuardarAPI(MethodView):
    """Guarda producto + receta completa en una sola transacción."""

    init_every_request = False

    def post(self):
        data = datos_json()

        try:
            producto, creado = _resolver_producto(data)

            if "nombre" in data:
                producto.nombre = _texto(data["nombre"], "nombre")

            if "valor" in data:
                producto.valor = _decimal(data["valor"], "valor")

            if "activo" in data:
                producto.activo = _booleano(data["activo"])

            if "insumos" in data:
                if not isinstance(data["insumos"], list):
                    raise ValueError("insumos debe ser una lista")

                db_session.execute(
                    delete(RecetaProducto).where(
                        RecetaProducto.productoId == producto.id
                    )
                )

                vistos = set()
                for item in data["insumos"]:
                    if not isinstance(item, dict):
                        raise ValueError("Cada insumo debe ser un objeto")

                    insumo = _resolver_insumo(item)
                    unidad = _resolver_unidad(item)
                    cantidad = _decimal(item.get("cantidad"), "cantidad", positivo=True)

                    clave = (insumo.id, unidad.id)
                    if clave in vistos:
                        raise ValueError(
                            f"El insumo {insumo.nombre} está repetido "
                            f"con la misma unidad de medida"
                        )
                    vistos.add(clave)

                    db_session.add(
                        RecetaProducto(
                            productoId=producto.id,
                            insumoId=insumo.id,
                            cantidad=cantidad,
                            unidadMedidaId=unidad.id,
                        )
                    )

            db_session.commit()
        except LookupError as exc:
            db_session.rollback()
            return jsonify({"error": str(exc)}), 404
        except (KeyError, ValueError, SQLAlchemyError) as exc:
            return respuesta_error(exc)

        db_session.expire_all()
        producto = db_session.get(Producto, producto.id)

        return jsonify(_producto_detalle(producto)), 201 if creado else 200


class ProductoDetalleAPI(MethodView):
    init_every_request = False

    def get(self, id):
        producto = db_session.get(Producto, id)

        if producto is None:
            return jsonify({"error": "No encontrado"}), 404

        return jsonify(_producto_detalle(producto))


def register_producto_panel(app):
    app.add_url_rule(
        "/producto/guardar",
        view_func=ProductoGuardarAPI.as_view("producto-guardar"),
        methods=["POST"],
    )
    app.add_url_rule(
        "/producto/<int:id>/detalle",
        view_func=ProductoDetalleAPI.as_view("producto-detalle"),
        methods=["GET"],
    )
