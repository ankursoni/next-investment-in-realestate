""" Module for realestate.com.au """

from typing import List

from bs4 import BeautifulSoup
from structlog import get_logger

from core.data_repository import Property

from ..data_source import City, DataSource, State


class RealEstate(DataSource):
    """Class for realestate.com.au"""

    buy_property_listing_url_template = (
        "https://www.realestate.com.au/buy/property-house-townhouse-with-{min_bedrooms}-between-"
        "{min_price}-{max_price}-in-{region},+{state}/list-{page}?includeSurrounding={include_surrounding}"
        "&activeSort=price-{sort_order_by_price}&source=refinement"
    )

    def get_property_listing_for_buying(
        self,
        min_bedrooms: int,
        min_price: int,
        max_price: int,
        city: City,
        state: State,
        include_surrounding: bool = False,
        sort_order_by_price: str = "asc",
    ) -> List[Property]:
        """Function to get property listing for buying."""

        logger = get_logger().bind(
            min_bedrooms=min_bedrooms,
            min_price=min_price,
            max_price=max_price,
            city=city,
            state=state,
            include_surrounding=include_surrounding,
            sort_order_by_price=sort_order_by_price,
        )
        logger.info("Starting get property listing")

        result = []

        regions = self._get_regions_from_city(city)
        for region in regions:
            page = 1
            url_template_values = {
                "min_bedrooms": min_bedrooms,
                "min_price": min_price,
                "max_price": max_price,
                "region": region,
                "state": state,
                "page": page,
                "include_surrounding": str(include_surrounding).lower(),
                "sort_order_by_price": sort_order_by_price,
            }
            url = self.buy_property_listing_url_template.format(**url_template_values)
            response = self._make_web_request(url)
            soup = BeautifulSoup(response.content)
            property_cards = soup.find_all("residential-card__content")
            for index, property_card in enumerate(property_cards):
                logger.debug("Starting parse of property listing card", index=index)
                price_card = property_card.find("property-price")

        logger.info("Completed get property listing")
        return result

    def _get_regions_from_city(self, city: City) -> List[str]:
        match city:
            case City.ADELAIDE:
                return ["adelaide greater region"]
