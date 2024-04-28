""" Module for data source. """

from abc import ABC, abstractmethod
from enum import StrEnum, auto

from pydantic.dataclasses import dataclass
from requests import request
from structlog import get_logger


class City(StrEnum):
    """Class for storing city enumeration."""

    ADELAIDE = auto()
    BRISBANE = auto()
    MELBOURNE = auto()
    PERTH = auto()
    SYDNEY = auto()


class State(StrEnum):
    """Class for storing state enumeration."""

    QLD = auto()
    NSW = auto()
    VIC = auto()
    SA = auto()
    WA = auto()


class PropertyType(StrEnum):
    """Class for storing state enumeration."""

    HOUSE = auto()
    TOWNHOUSE = auto()


@dataclass
class PropertySearch:
    """Class for property search."""

    city: City
    state: State
    region: str
    number_of_bedrooms: str
    number_of_bathrooms: str
    number_of_parking_lots: str | None
    number_of_living_areas: str | None
    floor_area_sqm: str | None
    land_area_sqm: str | None
    asking_price: str


class DataSource(ABC):
    """Class for storing provider objects."""

    @abstractmethod
    def get_property_listing_for_buying(
        self,
        min_bedrooms: int,
        min_price: int,
        max_price: int,
        city: City,
        state: State,
        include_surrounding: bool = False,
        sort_order_by_price: bool = True,
    ) -> list[PropertySearch]:
        """Function to get property listing for buying."""

    def _make_web_request(self, url: str, method: str = "GET") -> bytes | None:
        """Function to make web request."""

        logger = get_logger()
        logger.info("Starting make web request", url=url, method=method)

        response = request(method, url)
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
