# DataBase/database.py

from sqlalchemy import create_engine, event
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base


engine = create_engine(
    "sqlite:///instance/database.db",
)


@event.listens_for(engine, "connect")
def _activar_foreign_keys(dbapi_connection, connection_record):
    # SQLite no valida las foreign keys por defecto.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
)

Base = declarative_base()


def init_db():

    Base.metadata.create_all(
        bind=engine
    )