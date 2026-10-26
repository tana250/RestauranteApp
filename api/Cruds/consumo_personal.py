from ..Modelos.consumo_personal import ConsumoPersonal
from .crudGenerico import register_api


def register_consumo_personal(app):
    register_api(app, ConsumoPersonal, "consumoPersonal")
