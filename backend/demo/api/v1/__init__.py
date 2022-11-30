"""
FastAPI demo REST API version 1 routes
"""
from demo.api.v1 import route_login
from demo.api.v1 import route_users
from fastapi import APIRouter

api_router_v1 = APIRouter(prefix="/v1")

# Demo v1 REST Endpoints
api_router_v1.include_router(route_users.router, prefix="/users", tags=["User"])
api_router_v1.include_router(route_login.router, prefix="/login", tags=["Login"])
