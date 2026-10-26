from ..Modelos.metodos_pago import MetodoPago
from .crudGenerico import register_api


def register_metodos_pago(app):
    register_api(app, MetodoPago, "metodosPago")
