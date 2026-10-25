from ..Modelos.marcas import Marca
from .crudGenerico import register_api


def register_marcas(app):
    register_api(app, Marca, "marcas")
