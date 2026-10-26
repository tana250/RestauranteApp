from ..Modelos.producto_venta import ProductoVenta
from .crudGenerico import register_api


def register_producto_venta(app):
    register_api(app, ProductoVenta, "productoVenta")
