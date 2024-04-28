""" Module for providers. """

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
from structlog import get_logger

from core import config
from core.data_repositories.sqlite import SQLite
from core.data_repository import DataRepository
from core.data_source_wrapper import DataSourceWrapper
from core.data_source_wrappers.domain_wrapper import DomainWrapper
from core.data_source_wrappers.realestate_wrapper import RealEstateWrapper
from core.enum import DataRepositoryType, DataSourceType


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Providers:
    """Class for storing providers."""

    data_repository: DataRepository
    data_source_wrapper: DataSourceWrapper


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
        data_source_wrapper=_get_data_source_wrapper(config.CONFIG.data_source_type),
    )

    logger.info("Completed configure providers")


def _get_data_repository(enum_type: DataRepositoryType) -> DataRepository:
    match enum_type:
        case DataRepositoryType.SQLITE:
            return SQLite()


def _get_data_source_wrapper(enum_type: DataSourceType) -> DataSourceWrapper:
    match enum_type:
        case DataSourceType.REAL_ESTATE:
            return RealEstateWrapper()
        case DataSourceType.DOMAIN:
            return DomainWrapper()
