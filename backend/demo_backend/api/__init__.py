from demo_backend.api.v1.routes import route_celery
from demo_backend.api.v1.routes import route_jobs
from demo_backend.api.v1.routes import route_login
from demo_backend.api.v1.routes import route_users
from fastapi import APIRouter

api_router = APIRouter()

api_router.include_router(route_users.router, prefix="/users", tags=["Users"])
api_router.include_router(route_jobs.router, prefix="/job", tags=["Jobs"])
api_router.include_router(route_login.router, prefix="/login", tags=["Login"])
api_router.include_router(route_celery.router, prefix="/celery", tags=["Celery"])
