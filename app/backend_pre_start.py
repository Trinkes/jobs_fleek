import logging

from sqlalchemy import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.database import database_config, SessionLocal

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
def init(session: SessionLocal) -> None:
    try:
        with session as local_session:
            local_session.execute(text("select(1)"))
    except Exception as e:
        print(e)
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    init(database_config.session_local())

    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()