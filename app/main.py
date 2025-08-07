import time
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from starlette.responses import RedirectResponse, JSONResponse

from app import api_router
from app.core.config import settings
from app.core.database import setup_database, get_engine
from app.core.exceptions import ResourceNotFoundException

if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_database()
    yield
    await get_engine().dispose()


fastapi_app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

if settings.BACKEND_CORS_ORIGINS:
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

fastapi_app.include_router(api_router)


@fastapi_app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time * 1000:.2f} ms"
    return response


@fastapi_app.get("/", tags=["root"], include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")


@fastapi_app.exception_handler(ResourceNotFoundException)
def resource_not_found_exception_handler(request, exc: ResourceNotFoundException):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=exc.to_json())
