"""
Primary FastAPI startup
"""
from fastapi import FastAPI


def get_application() -> FastAPI:
    _app = FastAPI(title="Hello, FastPAI!", version="0.1.0")

    return _app


app = get_application()
