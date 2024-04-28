""" Module for api. """

import uvicorn
from fastapi import FastAPI
from structlog import get_logger

from core import config, main

app = FastAPI(title="Next Investment API", version="0.1.0")


@app.get("/")
async def get_root() -> dict[str, str]:
    """Get root path."""

    logger = get_logger()
    logger.info("Completed get root path - '/' from api")

    return {"message": "Welcome to API!"}


@app.post("/job")
async def post_job() -> str:
    """Post job path."""

    logger = get_logger()
    logger.info("Starting post job path - '/job' from api")

    logger.info("Completed post job path - '/job' from api")


@app.get("/job")
async def get_job(id_: str) -> str:
    """Get job path."""

    logger = get_logger()
    logger.info("Starting get job path - '/job' from api", id=id_)

    logger.info("Completed get job path - '/job' from api", id=id_)


def init() -> None:
    """Entry point if called as an executable."""

    logger = get_logger()
    logger.info("Starting init from api")

    main.init()
    uvicorn.run(
        "core.api:app",
        host="127.0.0.1",
        port=config.CONFIG.api_port,
        reload=config.CONFIG.api_reload,
    )

    logger.info("Completed init from api")


if __name__ == "__main__":
    init()
