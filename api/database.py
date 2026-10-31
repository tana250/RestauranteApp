# DataBase/database.py

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from sqlalchemy.schema import CreateTable


engine = None
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False))
Base = declarative_base()


def init_db(app=None):
    global engine

    if app is not None:
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI") or app.config.get("DATABASE_URI")
        if db_uri is None:
            db_uri = "sqlite:///instance/database.db"
    else:
        try:
            from flask import current_app

            db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI") or current_app.config.get(
                "DATABASE_URI"
            )
            if db_uri is None:
                db_uri = "sqlite:///instance/database.db"
        except Exception:
            db_uri = "sqlite:///instance/database.db"

    connect_args = {}
    if isinstance(db_uri, str) and db_uri.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        if ":///" in db_uri and ":memory:" not in db_uri:
            db_path = db_uri.split(":///")[-1]
            if db_path:
                db_dir = os.path.dirname(os.path.abspath(db_path))
                if db_dir and not os.path.exists(db_dir):
                    os.makedirs(db_dir, exist_ok=True)

    engine = create_engine(db_uri, connect_args=connect_args)

    @event.listens_for(engine, "connect")
    def _activar_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    db_session.configure(bind=engine)

    import api.Modelos  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrar_insumos_nullable()
    _migrar_unicidad()
    _migrar_egreso_mercaderia()
    _migrar_tablas_legacy()
    _migrar_hora()


def _migrar_unicidad():
    """
    SQLite no agrega UNIQUE CONSTRAINT a tablas ya existentes: se crean
    los indices unicos directamente.

    - ``recetas_productos``: clave compuesta (productoId, insumoId).
    - ``insumos``: clave compuesta (marcaId, nombre).
    """
    if engine is None or not engine.url.drivername.startswith("sqlite"):
        return

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.exec_driver_sql(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_recetas_producto_insumo "
            "ON recetas_productos (productoId, insumoId)"
        )
        conn.exec_driver_sql(
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_insumos_marca_nombre "
            "ON insumos (marcaId, nombre)"
        )


def _migrar_egreso_mercaderia():
    """
    SQLite no agrega columnas a tablas existentes con ALTER TABLE cuando la
    tabla usa claves foráneas complejas, así que se recrea ``egreso_mercaderia``
    para agregar ``ventaId`` (nullable: NULL indica consumo de personal).

    También agrega ``cantidad`` a ``productoVenta`` si la tabla todavía no la
    tiene (creada antes de incluir el campo).
    """
    if engine is None or not engine.url.drivername.startswith("sqlite"):
        return

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        columnas_egreso = {
            columna["name"]
            for columna in conn.exec_driver_sql(
                "PRAGMA table_info(egreso_mercaderia)"
            ).mappings().all()
        }

        if "ventaId" not in columnas_egreso:
            tabla = Base.metadata.tables["egreso_mercaderia"]
            ddl = str(CreateTable(tabla).compile(dialect=engine.dialect))
            ddl = ddl.replace(
                "CREATE TABLE egreso_mercaderia", "CREATE TABLE egreso_mercaderia_new", 1
            )

            conn.exec_driver_sql("PRAGMA foreign_keys=OFF")

            try:
                conn.exec_driver_sql("DROP TABLE IF EXISTS egreso_mercaderia_new")
                conn.exec_driver_sql(ddl)
                conn.exec_driver_sql(
                    "INSERT INTO egreso_mercaderia_new (id, ventaId, ingresoMercaderiaId, cantidad) "
                    "SELECT id, NULL, ingresoMercaderiaId, cantidad FROM egreso_mercaderia"
                )
                conn.exec_driver_sql("DROP TABLE egreso_mercaderia")
                conn.exec_driver_sql("ALTER TABLE egreso_mercaderia_new RENAME TO egreso_mercaderia")
            finally:
                conn.exec_driver_sql("PRAGMA foreign_keys=ON")

        columnas_producto_venta = {
            columna["name"]
            for columna in conn.exec_driver_sql(
                "PRAGMA table_info(producto_venta)"
            ).mappings().all()
        }

        if "cantidad" not in columnas_producto_venta:
            conn.exec_driver_sql(
                "ALTER TABLE producto_venta ADD COLUMN cantidad INTEGER NOT NULL DEFAULT 1"
            )


def _migrar_tablas_legacy():
    """
    SQLite no renombra tablas automaticamente al cambiar el metadata.

    Renombra las tablas creadas con nombres camelCase a los nombres
    snake_case del esquema (``schema.md``).
    """
    if engine is None or not engine.url.drivername.startswith("sqlite"):
        return

    tablas_legacy = {
        "consumoPersonal": "consumo_personal",
        "metodosPago": "metodos_pago",
        "productoVenta": "producto_venta",
    }

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for tabla_antigua, tabla_nueva in tablas_legacy.items():
            existe = (
                conn.exec_driver_sql(
                    f"SELECT name FROM sqlite_master "
                    f"WHERE type = 'table' AND name = '{tabla_antigua}'"
                ).scalar()
            )

            if existe:
                conn.exec_driver_sql(
                    f"ALTER TABLE {tabla_antigua} RENAME TO {tabla_nueva}"
                )


def _migrar_hora():
    """
    SQLite no agrega columnas NOT NULL a tablas existentes con ALTER
    TABLE si no se indica un default, así que se agregan las columnas
    ``hora`` (Time, NOT NULL) con un default y luego se reutilizan.

    Las entidades que ganaron el campo ``hora`` desacoplado de ``fecha``:
    ``ingreso_mercaderia``, ``venta``, ``consumo_personal`` y ``pagos``.
    """
    if engine is None or not engine.url.drivername.startswith("sqlite"):
        return

    columnas_nuevas = {
        "ingreso_mercaderia": "hora",
        "venta": "hora",
        "consumo_personal": "hora",
        "pagos": "hora",
    }

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for tabla, columna in columnas_nuevas.items():
            existentes = {
                columna_info["name"]
                for columna_info in conn.exec_driver_sql(
                    f"PRAGMA table_info({tabla})"
                ).mappings().all()
            }

            if columna in existentes:
                continue

            conn.exec_driver_sql(
                f"ALTER TABLE {tabla} ADD COLUMN {columna} TIME NOT NULL DEFAULT '00:00:00'"
            )


def _migrar_insumos_nullable():
    """
    SQLite no permite quitar NOT NULL con ALTER TABLE. Reconstruye
    ``insumos`` cuando fue creada con tipoInsumoId/marcaId obligatorios.

    Es necesario para crear insumos desde el panel de productos sin
    marca ni tipo (se completan después en el panel de insumos).
    """
    if engine is None or not engine.url.drivername.startswith("sqlite"):
        return

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        columnas = conn.exec_driver_sql("PRAGMA table_info(insumos)").mappings().all()

        if not columnas:
            return

        por_nombre = {columna["name"]: columna for columna in columnas}
        tipo = por_nombre.get("tipoInsumoId")
        marca = por_nombre.get("marcaId")

        if not tipo or not marca:
            return

        if not tipo["notnull"] and not marca["notnull"]:
            return

        tabla = Base.metadata.tables["insumos"]
        ddl = str(CreateTable(tabla).compile(dialect=engine.dialect))
        ddl = ddl.replace("CREATE TABLE insumos", "CREATE TABLE insumos_new", 1)

        conn.exec_driver_sql("PRAGMA foreign_keys=OFF")

        try:
            conn.exec_driver_sql("DROP TABLE IF EXISTS insumos_new")
            conn.exec_driver_sql(ddl)
            conn.exec_driver_sql(
                "INSERT INTO insumos_new (id, nombre, tipoInsumoId, marcaId) "
                "SELECT id, nombre, tipoInsumoId, marcaId FROM insumos"
            )
            conn.exec_driver_sql("DROP TABLE insumos")
            conn.exec_driver_sql("ALTER TABLE insumos_new RENAME TO insumos")
        finally:
            conn.exec_driver_sql("PRAGMA foreign_keys=ON")
