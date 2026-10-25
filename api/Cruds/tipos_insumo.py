from ..Modelos.tipos_insumo import TipoInsumo
from .crudGenerico import register_api


def register_tipos_insumo(app):
    register_api(app, TipoInsumo, "tiposInsumo")
