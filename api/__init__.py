from flask import Flask

from .Cruds.ingreso_mercaderia import register_ingreso_mercaderia
from .Cruds.insumos import register_insumos
from .Cruds.marcas import register_marcas
from .Cruds.producto import register_producto
from .Cruds.proveedor import register_proveedor
from .Cruds.receta_producto import register_recetas_productos
from .Cruds.tipos_insumo import register_tipos_insumo
from .Cruds.unidades_medida import register_unidades_medida
from .database import init_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY="dev",
            SQLALCHEMY_DATABASE_URI="sqlite:///instance/database.db",
            TESTING=False,
        )
    else:
        app.config.from_mapping(test_config)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        from .database import db_session

        db_session.remove()

    init_db(app)

    register_proveedor(app)
    register_unidades_medida(app)
    register_tipos_insumo(app)
    register_marcas(app)
    register_insumos(app)
    register_producto(app)
    register_ingreso_mercaderia(app)
    register_recetas_productos(app)

    return app
