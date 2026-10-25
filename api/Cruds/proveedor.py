from ..Modelos.proveedor import Proveedor
from .crudGenerico import register_api


def register_proveedor(app):
    register_api(app, Proveedor, "proveedor")
