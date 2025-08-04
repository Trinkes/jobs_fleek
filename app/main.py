import sentry_sdk
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from starlette.responses import RedirectResponse

from app import api_router
from app.core.config import settings



if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)

@app.get("/", tags=["root"], include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")