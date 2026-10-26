from ..Modelos.venta import Venta
from .crudGenerico import register_api


def register_venta(app):
    register_api(app, Venta, "venta")
