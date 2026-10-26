from ..Modelos.mozo import Mozo
from .crudGenerico import register_api


def register_mozo(app):
    register_api(app, Mozo, "mozo")
