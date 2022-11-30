"""See the following SQLAlchemy tutorial link for info about how the Base concept
populates the MetaData sub-object which in turn allows Alembic and SQLAlchemy to
maintain a concept of the global database schema.

https://docs.sqlalchemy.org/en/14/tutorial/metadata.html#defining-table-metadata-with-the-orm
"""
from typing import Optional

from demo.core.config import core_config
from fastapi.logger import logger
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import registry
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

logger.info(f"[autoai.database] Database URI being used: {core_config.DATABASE_URI}")

engine_default: Engine = create_engine(
    core_config.DATABASE_URI, pool_pre_ping=True, future=True
)
# NOTE: We're using the DATABASE_URI_GENERIC here. See the notes in core_config.
engine_generic: Engine = create_engine(
    core_config.DATABASE_URI_GENERIC,
    isolation_level="AUTOCOMMIT",
    echo=True,
    future=True,
)
SessionLocal: sessionmaker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_default,
    future=True,
)

mapper_registry = registry()


class Base(metaclass=DeclarativeMeta):
    """
    Shared class for all SQLAlchemy models in order to maintain a shared MetaData
    instance used by Alembic in general and Pytest specifically when calling
    `Base.metadata.drop_all(engine_default)` or `...create_all(engine_default)`

    This is used instead of the simpler Base=declarative_base() in order to provide more
    explicit instantiation that works better with intellisense-like helpers in VSCode,
    PyCharm, etc.

    This is boilerplate from the SQLAlchemy recommendation at
    https://docs.sqlalchemy.org/en/14/orm/mapping_api.html?highlight=declarative_base
    #sqlalchemy.orm.registry.generate_base
    """

    __abstract__ = True
    registry = mapper_registry
    metadata = mapper_registry.metadata

    __init__ = mapper_registry.constructor


def get_db() -> Session:
    """
    Attempt to generate a new SQLAlchemy Session using the SessionLocal sessionmaker
    generator.
    """
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logger.error(e)
    finally:
        if db:
            db.close()
