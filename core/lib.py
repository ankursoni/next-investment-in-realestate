""" Module for library functions. """

import argparse
import dataclasses
import json
import logging
import os
import re
from datetime import UTC, datetime
from enum import StrEnum

import structlog
from pydantic.dataclasses import dataclass
from structlog import get_logger

from core import config
from core.enum import DataRepositoryType, DataSourceType


@dataclass
class CLIArgs:
    """Class for command line interface (cli) arguments."""

    debug_mode: bool = False
    api_port: int = 8080
    api_reload: bool = False
    data_repository_type: DataRepositoryType = DataRepositoryType.SQLITE
    run_db_migrations: bool = True
    data_source_type: DataSourceType = DataSourceType.REAL_ESTATE


def parse_cli_args_with_defaults() -> CLIArgs:
    """Parse cli arguments with defaults."""

    logger = get_logger()
    logger.info("Starting parse cli arguments with defaults")

    parser = argparse.ArgumentParser(description="CLI arguments")
    parser.add_argument(
        "--debug-mode", help="Enable debug mode logging: false (default)"
    )
    parser.add_argument("--api-port", help="API port: 8080 (default)")
    parser.add_argument("--api-reload", help="API reload: false (default)")
    parser.add_argument(
        "--data-repository-type",
        help="Data repository type: sqlite (default) or mongodb",
    )
    parser.add_argument(
        "--data-source-type", help="Data source type: realestate (default) or domain"
    )
    parser.add_argument("--run-db-migrations", help="Run db migrations: true (default)")
    args = parser.parse_args()
    logger.info("Passed cli arguments", args=args)

    cli_args = {
        "debug_mode": json.loads(args.debug_mode) if args.debug_mode else None,
        "api_port": args.api_port if args.api_port else None,
        "api_reload": json.loads(args.api_reload) if args.api_reload else None,
        "data_repository_type": (
            parse_strenum_from_string(DataRepositoryType, args.data_repository_type)
            if args.data_repository_type
            else None
        ),
        "run_db_migrations": (
            json.loads(args.run_db_migrations) if args.run_db_migrations else None
        ),
        "data_source_type": (
            parse_strenum_from_string(DataSourceType, args.data_source_type)
            if args.data_source_type
            else None
        ),
    }
    result = CLIArgs(
        **{arg: value for arg, value in cli_args.items() if value is not None}
    )

    logger.info("Completed parse cli arguments with defaults", result=result)
    return result


@dataclass
class EnvVars:
    """Class for environment variables."""

    sqlite_connection_string: str = "sqlite+pysqlite:///local/local.sqlite3"


def parse_env_vars_with_defaults() -> EnvVars:
    """Parse environment variables with defaults."""

    logger = get_logger()
    logger.info("Starting parse environment variables with defaults")

    env_vars = {
        "sqlite_connection_string": os.getenv("SQLITE_CONNECTION_STRING"),
    }
    result = EnvVars(
        **{env: value for env, value in env_vars.items() if value is not None}
    )
    logger.debug("Parsed environment variables", result=result)

    logger.info("Completed parse environment variables with defaults")
    return result


def parse_strenum_from_string(enum_type: StrEnum, value: str) -> any:
    """Parse string enum from string value."""

    logger = get_logger().bind(enum_type=enum_type, value=value)
    logger.info("Starting parse string enum from string value")

    if (
        (enum_type is None or not issubclass(enum_type, StrEnum))
        or value is None
        or value.strip() == ""
    ):
        logger.warning(
            "Unable to parse string enum from string value as it is not proper"
        )
        return None

    uppercase_value = value.upper().strip()
    result = None
    if hasattr(enum_type, uppercase_value):
        result = enum_type[uppercase_value]
    else:
        logger.warning(
            "Unable to parse string enum from string value as it is not found"
        )

    logger.info(
        "Completed parse string enum from string value",
        result=result,
    )
    return result


def configure_global_logging_level(debug_mode) -> logging.Logger:
    """Configure global logging level."""

    logger = get_logger().bind(debug_mode=debug_mode)
    logger.info("Starting configure global logging level")

    logging_level = logging.DEBUG if debug_mode else logging.INFO
    structlog.configure_once(
        wrapper_class=structlog.make_filtering_bound_logger(logging_level),
    )
    if debug_mode:
        logger.debug("Global logging level is set as DEBUG")
    else:
        logger.info("Global logging level is set as INFO")

    logger.info("Completed configure global logging level")


def log_config_settings(conf: config.Config) -> None:
    """Log configuration settings in debug mode."""

    logger = get_logger()
    logger.debug("Starting log configuration settings in debug mode")

    for key, value in dataclasses.asdict(conf).items():
        logger.debug(key, value=str(value))

    logger.debug("Completed log configuration settings in debug mode")


def now_utc() -> datetime:
    """Datetime now in UTC."""

    return datetime.now(UTC)


def keep_only_numbers(input_string: str) -> str:
    """Keep only numbers"""
    return re.sub(r"[^0-9]", "", input_string)
