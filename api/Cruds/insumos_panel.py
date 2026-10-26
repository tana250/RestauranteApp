from flask import jsonify
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError

from ..database import db_session
from ..Modelos.insumos import Insumo
from ..Modelos.marcas import Marca
from ..Modelos.tipos_insumo import TipoInsumo
from .crudGenerico import datos_json, respuesta_error


def _entero(valor, campo):
    try:
        return int(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{campo} debe ser un entero")


def _id_opcional(valor, campo, modelo):
    if valor in (None, ""):
        return None

    id_relacionado = _entero(valor, campo)
    if db_session.get(modelo, id_relacionado) is None:
        raise ValueError(f"{campo} no existe")
    return id_relacionado


class InsumosGuardarAPI(MethodView):
    """Actualiza marca y tipo de varios insumos en una transacción."""

    init_every_request = False

    def patch(self):
        data = datos_json()
        filas = data.get("insumos")

        if not isinstance(filas, list):
            return jsonify({"error": "insumos debe ser una lista"}), 400

        try:
            vistos = set()
            actualizados = []

            for fila in filas:
                if not isinstance(fila, dict):
                    raise ValueError("Cada insumo debe ser un objeto")

                insumo_id = _entero(fila.get("id"), "id")
                if insumo_id in vistos:
                    raise ValueError(f"El insumo {insumo_id} está repetido")
                vistos.add(insumo_id)

                insumo = db_session.get(Insumo, insumo_id)
                if insumo is None:
                    raise ValueError(f"El insumo {insumo_id} no existe")

                if "marcaId" in fila:
                    insumo.marcaId = _id_opcional(
                        fila.get("marcaId"),
                        "marcaId",
                        Marca,
                    )

                if "tipoInsumoId" in fila:
                    insumo.tipoInsumoId = _id_opcional(
                        fila.get("tipoInsumoId"),
                        "tipoInsumoId",
                        TipoInsumo,
                    )

                actualizados.append(insumo)

            db_session.commit()
        except (KeyError, ValueError, SQLAlchemyError) as exc:
            return respuesta_error(exc)

        return jsonify([insumo.to_json() for insumo in actualizados])


def register_insumos_panel(app):
    app.add_url_rule(
        "/insumos/guardar",
        view_func=InsumosGuardarAPI.as_view("insumos-guardar"),
        methods=["PATCH"],
    )
