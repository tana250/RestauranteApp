from ..Modelos.mesa import Mesa
from .crudGenerico import register_api


def register_mesa(app):
    register_api(app, Mesa, "mesa")
