from ..Modelos.ingreso_mercaderia import IngresoMercaderia
from .crudGenerico import register_api


def register_ingreso_mercaderia(app):
    register_api(app, IngresoMercaderia, "ingresoMercaderia")
