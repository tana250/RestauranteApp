from ..Modelos.egreso_mercaderia import EgresoMercaderia
from .crudGenerico import register_api


def register_egreso_mercaderia(app):
    register_api(app, EgresoMercaderia, "egresoMercaderia")
