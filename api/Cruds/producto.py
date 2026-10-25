from ..Modelos.producto import Producto
from .crudGenerico import register_api


def register_producto(app):
    register_api(app, Producto, "producto")
