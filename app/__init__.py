from fastapi import APIRouter

from app.media.api.media_router import media_router
from app.tools.tools_router import tools_router

api_router = APIRouter()
api_router.include_router(media_router, prefix="/media", tags=["media"])
api_router.include_router(tools_router, prefix="/tools", tags=["tools"])
