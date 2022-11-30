"""
Primary FastAPI application instance creation
"""
from demo.version import __version__
from fastapi import FastAPI


def get_application() -> FastAPI:
    """
    FastAPI application creation entrypoint
    """
    _app = FastAPI(title="Hello, FastAPI!", version=__version__)

    return _app


app = get_application()
