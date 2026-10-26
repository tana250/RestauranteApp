from ..Modelos.personal import Personal
from .crudGenerico import register_api


def register_personal(app):
    register_api(app, Personal, "personal")
