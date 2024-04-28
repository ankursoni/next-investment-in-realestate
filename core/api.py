""" Module for api. """

import uvicorn
from fastapi import FastAPI
from structlog import get_logger

from core import config, main

main.init()

app = FastAPI(title="Next Investment API", version="0.1.0")


@app.get("/")
async def get_root() -> dict[str, str]:
    """Get root path."""

    logger = get_logger()
    logger.info("Completed get root path - '/' from api")

    return {"msg": "Welcome to API!"}


@app.post("/job")
async def post_job() -> str:
    """Post job."""

    logger = get_logger()
    logger.info("Starting post job - '/job' from api")

    logger.info("Completed post job - '/job' from api")


@app.get("/job/{job_id}")
async def get_job(job_id: str) -> dict[str, str]:
    """Get job."""

    logger = get_logger().bind(job_id=str(job_id))
    logger.info("Starting get job - '/job' from api", job_id=job_id)

    logger.info("Completed get job - '/job' from api")


def init() -> None:
    """Entry point if called as an executable."""

    logger = get_logger()
    logger.info("Starting init from api")

    # configure uvicorn logging formatters
    uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
    uvicorn_log_default_formatter = uvicorn_log_config["formatters"]["default"]
    uvicorn_log_default_formatter["fmt"] = "%(asctime)s [%(levelprefix)s] %(message)s"
    uvicorn_log_access_formatter = uvicorn_log_config["formatters"]["access"]
    uvicorn_log_access_formatter["fmt"] = (
        '%(asctime)s [%(levelprefix)s] %(client_addr)s - "%(request_line)s" %(status_code)s'
    )
    uvicorn_log_access_formatter["datefmt"] = uvicorn_log_default_formatter[
        "datefmt"
    ] = "%Y-%m-%d %H:%M:%S"

    # run uvicorn
    uvicorn.run(
        "core.api:app",
        host="127.0.0.1",
        port=config.CONFIG.api_port,
        reload=config.CONFIG.api_reload,
        log_level="debug" if config.CONFIG.debug_mode else "info",
    )

    logger.info("Completed init from api")


if __name__ == "__main__":
    init()
