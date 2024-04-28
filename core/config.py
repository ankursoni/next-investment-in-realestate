""" Module for configuration settings. """

from pydantic.dataclasses import dataclass

from core.enum import DataRepositoryType, DataSourceType


@dataclass
class Config:
    """Class for storing configuration settings."""

    # cli args
    debug_mode: bool
    data_repository_type: DataRepositoryType
    run_db_migrations: bool

    # api
    api_port: int
    api_reload: bool

    # sqlite
    sqlite_connection_string: str

    # data source
    data_source_type: DataSourceType


CONFIG: Config = None
