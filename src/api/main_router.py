from fastapi import APIRouter
from src.api.routes import mining, analytics, admin

api_router = APIRouter()

api_router.include_router(mining.router)
api_router.include_router(analytics.router)
api_router.include_router(admin.router)