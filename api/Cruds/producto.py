from sqlalchemy import delete

from ..database import db_session
from ..Modelos.producto import Producto
from ..Modelos.receta_producto import RecetaProducto
from .crudGenerico import register_api


def _borrar_receta(producto):
    db_session.execute(
        delete(RecetaProducto).where(RecetaProducto.productoId == producto.id)
    )


def register_producto(app):
    register_api(app, Producto, "producto", on_delete=_borrar_receta)
