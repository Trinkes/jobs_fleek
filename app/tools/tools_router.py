import logging

from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import text
from starlette import status

from app.core.database import AsyncSessionDep
from app.tasks.celery_tasks import celery_health_check

tools_router = APIRouter()


@tools_router.get("/status")
async def health_check(db_session: AsyncSessionDep):
    async with db_session() as session:
        try:
            if list((await session.execute(text("select 1"))))[0][0] != 1:
                raise HTTPException(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="unable to connect to database",
                )
        except Exception as error:
            logging.error("unable to connect to database", exc_info=error)
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="unable to connect to database",
            )
        return {"status": "OK"}


@tools_router.get("/tools/celery_status")
def celery_status(message: str | None = None):
    result = celery_health_check.apply_async(kwargs={"message": message})
    try:
        response = result.get(timeout=5)
    except Exception as error:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"message": "celery not working", "response": jsonable_encoder(error)},
        )

    if response["statusCode"] != 200:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"message": "celery not working", "response": response},
        )
    return response
