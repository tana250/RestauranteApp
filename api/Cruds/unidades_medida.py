from ..Modelos.unidades_medida import UnidadMedida
from .crudGenerico import register_api


def register_unidades_medida(app):
    register_api(app, UnidadMedida, "unidadesMedida")
