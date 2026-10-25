from ..Modelos.receta_producto import RecetaProducto
from .crudGenerico import register_api


def register_recetas_productos(app):
    register_api(app, RecetaProducto, "recetasProductos")
