""" Module for providers. """

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from structlog import get_logger

from core import config
from core.config import DataRepositoryType, DataSourceType
from core.data_repositories.sqlite import SQLite
from core.data_repository import DataRepository
from core.data_source import DataSource
from core.data_sources.domain import Domain
from core.data_sources.realestate import RealEstate


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Providers:
    """Class for storing providers."""

    data_repository: DataRepository
    data_source: DataSource


PROVIDERS: Providers = None


def configure_providers() -> None:
    """Configure providers."""

    logger = get_logger().bind(
        DataRepositoryType=config.CONFIG.data_repository_type,
        DataSourceType=config.CONFIG.data_source_type,
    )
    logger.info("Starting configure providers")
    global PROVIDERS
    PROVIDERS = Providers(
        data_repository=_get_data_repository(config.CONFIG.data_repository_type),
        data_source=_get_data_source(config.CONFIG.data_source_type),
    )

    logger.info("Completed configure providers")


def _get_data_repository(enum_type: DataRepositoryType) -> DataRepository:
    match enum_type:
        case DataRepositoryType.SQLITE:
            return SQLite()


def _get_data_source(enum_type: DataSourceType) -> DataSource:
    match enum_type:
        case DataSourceType.REAL_ESTATE:
            return RealEstate()
        case DataSourceType.DOMAIN:
            return Domain()
