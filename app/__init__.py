from fastapi import APIRouter

from app.tools.tools_router import tools_router

api_router = APIRouter()
api_router.include_router(tools_router, prefix="/tools", tags=["tools"])