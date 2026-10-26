from ..Modelos.pagos import Pago
from .crudGenerico import register_api


def register_pagos(app):
    register_api(app, Pago, "pagos")
