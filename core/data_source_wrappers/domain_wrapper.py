""" Module for domain.com.au wrapper. """

from typing import List

from core.data_repository import Property
from core.data_source_wrapper import DataSourceWrapper
from core.enum import City, ListingType, PropertyType, State


class DomainWrapper(DataSourceWrapper):
    """Class for domain.com.au wrapper."""

    def get_property_listing(
        self,
        listing_type: ListingType,
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
        pause_range: tuple[int, int] = (1, 5),
    ) -> List[Property]:
        """Function to get property listing."""
