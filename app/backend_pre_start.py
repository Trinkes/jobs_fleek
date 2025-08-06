import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.database import AsyncSessionLocal, setup_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init(session: async_sessionmaker[AsyncSessionLocal]) -> None:
    try:
        async with session() as local_session:
            await local_session.execute(text("select(1)"))
    except Exception as e:
        print(e)
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    asyncio.run(init(setup_database()))
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
