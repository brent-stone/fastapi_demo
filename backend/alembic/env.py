from logging import getLogger
from logging import INFO
from logging.config import fileConfig

from alembic import context
from demo_backend.core.config import core_config
from demo_backend.database import Base
from demo_backend.database import engine_default
from demo_backend.database import engine_generic
from demo_backend.database import engine_user
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.schema import MetaData

getLogger("sqlalchemy.engine").setLevel(INFO)

logger = getLogger(__name__)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
target_metadata: MetaData = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def detect_and_create_new_db(a_engine: Engine, a_database: str) -> None:
    """
    Attempt to connect to the <a_database> database. If it doesn't exist (likely if this is
    the first time connecting or running tests), create it.
    """
    try:
        with a_engine.connect():
            pass
    except OperationalError:
        logger.info(f"Database {a_database} wasn't found. Attempting to create it.")
        # NOTE: We're using the engine_generic here. See the notes in core_config.
        try:
            with engine_generic.connect() as l_connection:
                l_connection.execute(f"CREATE DATABASE {a_database}")
                logger.info(f"Created database {a_database}")
        except OperationalError as e:
            logger.error(
                f"Failed to create database {a_database} using generic URI {str(engine_generic)}: {e}"
            )


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    logger.info("Running Alembic migration online.")
    logger.info(f"SQLAlchemy metadata tables: {list(target_metadata.tables)}")

    # Ensure the default postgres user:pass combo has an associated database for the user so Postgres is happy
    # detect_and_create_new_db(engine_user, core_config.POSTGRES_USER)

    # Ensure the primary database is created if it doesn't already exist
    detect_and_create_new_db(engine_default, core_config.POSTGRES_DB)
    #
    # # Attempt to connect to the main database. If it doesn't exist (likely if this is
    # # the first time connecting or running tests), create it.
    # try:
    #     with engine_default.connect() as l_connection:
    #         pass
    # except OperationalError:
    #     logger.info(
    #         f"Database {core_config.POSTGRES_DB} wasn't found. Attempting to \
    #             create it."
    #     )
    #     # NOTE: We're using the engine_generic here. See the notes in core_config.
    #     with engine_generic.connect() as l_connection:
    #         l_connection.execute(f"CREATE DATABASE {core_config.POSTGRES_DB}")

    l_engine: Engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=core_config.DATABASE_URI,
        echo=True,
    )

    with l_engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode. This mode is to simply print any
    SQL queries that would have otherwise been sent to the database.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    logger.info("Running Alembic migration offline.")
    logger.info(f"SQLAlchemy metadata tables: {list(target_metadata.tables)}")

    context.configure(
        url=core_config.DATABASE_URI,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
