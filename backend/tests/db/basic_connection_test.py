# """Basic tests to ensure pytest is able to connect to the postgres database and the
# testing database/tables are created.
# """
# from logging import getLogger
# from demo_backend.core.config import core_config
# from demo_backend.core.config import testing_postfix_str
# from demo_backend.database import Base
# from demo_backend.database import engine_default
# from sqlalchemy.engine import Connection
# from sqlalchemy.exc import SQLAlchemyError
# from sqlalchemy.schema import MetaData
# logger = getLogger(__name__)
# def test_db_name() -> None:
#     """Test whether environment variables were successfully loaded into core_config
#     and that the POSTGRES_DB and POSTGRES_URI reflect the testing postfix string.
#     """
#     assert testing_postfix_str in core_config.POSTGRES_DB
#     assert testing_postfix_str in core_config.DATABASE_URI
# def test_db_connection() -> None:
#     """Test whether an attempt to connect to the postgres database is successful"""
#     try:
#         with engine_default.connect() as connection:
#             assert isinstance(connection, Connection)
#             assert True
#     except SQLAlchemyError as e:
#         logger.error(e.__cause__)
#         assert False
# def test_db_metadata() -> None:
#     """Test that the SQLAlchemy ORM metadata includes tables via inheratance from
#     the Base declared in demo_backend.database
#     """
#     l_metadata: MetaData = Base.metadata
#     l_has_tables: bool = False
#     for t in l_metadata.sorted_tables:
#         logger.info(f"[Table name] columns: [{t.name}] {t.columns.keys()}")
#         l_has_tables = True
#     assert l_has_tables
