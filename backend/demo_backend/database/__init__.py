"""See the following SQLAlchemy tutorial link for info about how the Base concept
populates the MetaData sub-object which in turn allows Alembic and SQLAlchemy to
maintain a concept of the global database schema.

https://docs.sqlalchemy.org/en/14/tutorial/metadata.html#defining-table-metadata-with-the-orm
"""
# from typing import Any
from typing import Generator, Optional

from demo_backend.core.config import core_config
from fastapi.logger import logger
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

# from sqlalchemy.schema import MetaData

logger.info(
    f"[demo_backend.database] Database URI being used: {core_config.DATABASE_URI}"
)

engine_default: Engine = create_engine(core_config.DATABASE_URI, pool_pre_ping=True)
# NOTE: We're using the DATABASE_URI_GENERIC here. See the notes in core_config.
engine_generic: Engine = create_engine(
    core_config.DATABASE_URI_GENERIC, isolation_level="AUTOCOMMIT", echo=True
)
# NOTE: We're using the DATABASE_URI_USER here. See the notes in core_config.
engine_user: Engine = create_engine(core_config.DATABASE_URI_USER, pool_pre_ping=True)

SessionLocal: sessionmaker = sessionmaker(
    autocommit=False, autoflush=False, bind=engine_default
)


Base = declarative_base()


def get_db() -> Session:
    """
    On demand, create a new SQLAlchemy database Session. Primarily used for FastAPI dependency injection within routes.
    """
    db: Optional[Session] = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logger.error(e)
    finally:
        if db is not None:
            db.close()
