from ..Modelos.insumos import Insumo
from .crudGenerico import register_api


def register_insumos(app):
    register_api(app, Insumo, "insumos")
