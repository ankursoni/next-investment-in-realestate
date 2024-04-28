""" Module for configuration settings. """

from enum import StrEnum, auto

from pydantic.dataclasses import dataclass


class DataRepositoryType(StrEnum):
    """Class for storing data repository type enumeration."""

    SQLITE = auto()


class DataSourceType(StrEnum):
    """Class for storing data source type enumeration."""

    REAL_ESTATE = auto()
    DOMAIN = auto()


@dataclass
class Config:
    """Class for storing configuration settings."""

    # cli args
    debug_mode: bool
    data_repository_type: DataRepositoryType
    run_sql_migrations: bool

    # api
    api_port: int
    api_reload: bool

    # sqlite
    sqlite_connection_string: str

    # data source
    data_source_type: DataSourceType


CONFIG: Config = None
