""" Module for domain.com.au """

from ..data_source import City, DataSource, State


class Domain(DataSource):
    """Class for domain.com.au"""

    def get_property_listing(
        self,
        min_: int,
        max_: int,
        city: City,
        state: State,
        include_surrounding: bool = False,
        sort_order_by_price: str = "asc",
    ):
        pass
