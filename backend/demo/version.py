"""This creates a second source of truth beyond pyproject.toml which is not great.
However, this is the simplest workaround for ensuring a __version__ string is available
to FastAPI app startup in both dev and prod.
Note that core_config.PROJECT_VERSION comes from an environment variable likely set by
docker-compose reading from a .env file.
"""
# from demo.core.config import core_config
#
# __version__: str = core_config.PROJECT_VERSION
