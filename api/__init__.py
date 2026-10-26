from flask import Flask
from flask_cors import CORS

from .Cruds.consumo_personal import register_consumo_personal
from .Cruds.egreso_mercaderia import register_egreso_mercaderia
from .Cruds.ingreso_mercaderia import register_ingreso_mercaderia
from .Cruds.ingreso_mercaderia_panel import register_ingreso_mercaderia_panel
from .Cruds.insumos import register_insumos
from .Cruds.insumos_panel import register_insumos_panel
from .Cruds.marcas import register_marcas
from .Cruds.mesa import register_mesa
from .Cruds.metodos_pago import register_metodos_pago
from .Cruds.mozo import register_mozo
from .Cruds.pagos import register_pagos
from .Cruds.personal import register_personal
from .Cruds.producto import register_producto
from .Cruds.producto_panel import register_producto_panel
from .Cruds.producto_venta import register_producto_venta
from .Cruds.proveedor import register_proveedor
from .Cruds.receta_producto import register_recetas_productos
from .Cruds.tipos_insumo import register_tipos_insumo
from .Cruds.unidades_medida import register_unidades_medida
from .Cruds.venta import register_venta
from .Cruds.venta_panel import register_venta_panel
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

    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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
    register_insumos_panel(app)
    register_producto(app)
    register_producto_panel(app)
    register_ingreso_mercaderia(app)
    register_ingreso_mercaderia_panel(app)
    register_recetas_productos(app)
    register_personal(app)
    register_mozo(app)
    register_mesa(app)
    register_egreso_mercaderia(app)
    register_venta(app)
    register_venta_panel(app)
    register_producto_venta(app)
    register_consumo_personal(app)
    register_metodos_pago(app)
    register_pagos(app)

    return app
