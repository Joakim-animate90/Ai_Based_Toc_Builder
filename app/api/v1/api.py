from fastapi import APIRouter
from app.api.v1.endpoints import toc

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(toc.router, prefix="/toc", tags=["toc"])
