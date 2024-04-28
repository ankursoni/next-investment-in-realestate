""" Module for data source wrapper. """

from abc import ABC, abstractmethod

from requests import request
from structlog import get_logger

from core.data_repository import Property
from core.enum import City, PropertyType, State


class DataSourceWrapper(ABC):
    """Class for data sources wrapper."""

    NOT_AVAILABLE = "<NA>"

    @abstractmethod
    def get_property_listing(
        self,
        is_renting: bool,
        property_types: list[PropertyType],
        min_bedrooms: int | None,
        min_price: int | None,
        max_price: int | None,
        city: City,
        state: State,
        include_surrounding: bool = False,
        sort_order_by_price: str = "asc",
        start_page: int = 1,
        end_page: int | None = 10000,
    ) -> list[Property]:
        """Function to get property listing for buying."""

    def _make_web_request(
        self, url: str, method: str = "GET", headers: dict = None
    ) -> bytes | None:
        """Function to make web request."""

        logger = get_logger()
        logger.info(
            "Starting make web request", url=url, method=method, headers=headers
        )

        response = request(method, url, headers=headers)
        if response.status_code != 200:
            logger.error(
                "Completed make web request",
                url=url,
                response_status_code=response.status_code,
            )
            raise Exception(
                f"Error: request failed with response status code: {response.status_code}"
            )

        logger.info("Completed make web request", url=url, method=method)
        return response
