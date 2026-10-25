# DataBase/database.py

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base


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
