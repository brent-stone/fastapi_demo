"""
Primary FastAPI application instance creation
"""
from fastapi import FastAPI


def get_application() -> FastAPI:
    """
    FastAPI application creation entrypoint
    """
    _app = FastAPI(title="Hello, FastAPI!", version="0.1.0")

    return _app


app = get_application()
