from flask import jsonify, request
from flask.views import MethodView
from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)

from ..database import db_session


def respuesta_error(exc):
    """
    Convierte una excepción de la vista en una
    respuesta JSON (con rollback de la sesión).
    """
    db_session.rollback()

    if isinstance(exc, KeyError):
        return jsonify({
            "error": f"Falta el campo {exc.args[0]}",
        }), 400

    if isinstance(exc, ValueError):
        return jsonify({
            "error": str(exc),
        }), 400

    if isinstance(exc, IntegrityError):
        return jsonify({
            "error": str(exc.orig),
        }), 409

    # Cualquier otro error de SQLAlchemy: 500 en JSON.
    return jsonify({
        "error": str(exc),
    }), 500


def datos_json():
    """
    Body de la request como dict.

    Si no hay JSON válido devuelve {} para que la
    validación de campos devuelva un 400 en JSON
    en vez de un 415/400 en HTML.
    """
    return request.get_json(silent=True) or {}


class ItemAPI(MethodView):

    init_every_request = False

    def __init__(self, model):
        self.model = model

    def _get_item(self, id):

        return db_session.scalar(
            select(self.model).where(
                self.model.id == id
            )
        )

    def get(self, id):

        item = self._get_item(id)

        if item is None:
            return jsonify({
                "error": "No encontrado"
            }), 404

        return jsonify(
            item.to_json()
        )

    def patch(self, id):

        item = self._get_item(id)

        if item is None:
            return jsonify({
                "error": "No encontrado"
            }), 404

        data = datos_json()

        try:
            item.update_from_json(data)
            db_session.commit()
        except (KeyError, ValueError, SQLAlchemyError) as exc:
            return respuesta_error(exc)

        return jsonify(
            item.to_json()
        )

    def delete(self, id):

        item = self._get_item(id)

        if item is None:
            return jsonify({
                "error": "No encontrado"
            }), 404

        try:
            db_session.delete(item)
            db_session.commit()
        except (KeyError, ValueError, SQLAlchemyError) as exc:
            return respuesta_error(exc)

        return "", 204


class GroupAPI(MethodView):

    init_every_request = False

    def __init__(self, model, on_create=None, load=()):
        self.model = model
        self.on_create = on_create
        self.load = load

    def get(self):

        stmt = select(self.model).options(
            *self.load
        )

        activo = request.args.get("activo")

        if activo is not None:

            if not hasattr(self.model, "activo"):
                return jsonify({
                    "error": "Este recurso no soporta "
                             "el filtro activo",
                }), 400

            if activo not in ("true", "false"):
                return jsonify({
                    "error": "activo debe ser true o false",
                }), 400

            stmt = stmt.where(
                self.model.activo.is_(activo == "true")
            )

        items = db_session.scalars(stmt).all()

        return jsonify([
            item.to_json()
            for item in items
        ])

    def post(self):

        data = datos_json()

        try:
            item = self.model.from_json(data)

            db_session.add(item)

            # Asigna el id antes de crear registros
            # hijos que lo referencien.
            db_session.flush()

            if self.on_create:
                self.on_create(item, data)

            # Una sola escritura: o se crea todo,
            # o no se crea nada.
            db_session.commit()
        except (KeyError, ValueError, SQLAlchemyError) as exc:
            return respuesta_error(exc)

        return jsonify(
            item.to_json()
        ), 201


def register_api(
    app,
    model,
    name,
    on_create=None,
    load=(),
    item=True,
):

    group = GroupAPI.as_view(
        f"{name}-group",
        model,
        on_create,
        load,
    )

    app.add_url_rule(
        f"/{name}/",
        view_func=group,
        methods=[
            "GET",
            "POST",
        ],
    )

    # Models sin id numérico (clave compuesta)
    # no pueden usar ItemAPI.
    if not item:
        return

    item_view = ItemAPI.as_view(
        f"{name}-item",
        model,
    )

    app.add_url_rule(
        f"/{name}/<int:id>",
        view_func=item_view,
        methods=[
            "GET",
            "PATCH",
            "DELETE",
        ],
    )