from unittest.mock import ANY

import core
from core import config
from core.data_repositories.sqlite import SQLite
from core.data_repository import Property
from core.data_source_wrappers.realestate_wrapper import RealEstateWrapper
from core.enum import (
    City,
    DataRepositoryType,
    DataSourceType,
    ListingType,
    PropertyType,
    State,
)

PROPERTIES: list[Property]


class TestRealestate:
    """Test search property from realestate."""

    def test_realestate_get_property_listing_for_buying(self, mocker):
        # arrange
        mocker.patch(
            "core.data_source_wrapper.request",
            TestRealestate._mock_realestate_buy_property_search_requests_get,
        )
        spy_request = mocker.spy(core.data_source_wrapper, "request")
        real_estate = RealEstateWrapper()

        # act
        global PROPERTIES
        PROPERTIES = real_estate.get_property_listing(
            ListingType.BUY,
            [PropertyType.HOUSE, PropertyType.TOWNHOUSE],
            3,
            400000,
            500000,
            City.ADELAIDE,
            State.SA,
            end_page=3,
            pause_range=(0, 0),
        )

        # assert
        spy_request.call_count = 3
        spy_request.assert_any_call(
            "GET",
            url="https://www.realestate.com.au/buy/property-house-townhouse-with-3-bedrooms-between-400000-500000-in-adelaide greater region,+sa/"
            "list-1?includeSurrounding=false&activeSort=price-asc&source=refinement",
            headers=ANY,
        )
        spy_request.assert_any_call(
            "GET",
            url="https://www.realestate.com.au/buy/property-house-townhouse-with-3-bedrooms-between-400000-500000-in-adelaide greater region,+sa/"
            "list-2?includeSurrounding=false&activeSort=price-asc&source=refinement",
            headers=ANY,
        )
        spy_request.assert_any_call(
            "GET",
            url="https://www.realestate.com.au/buy/property-house-townhouse-with-3-bedrooms-between-400000-500000-in-adelaide greater region,+sa/"
            "list-3?includeSurrounding=false&activeSort=price-asc&source=refinement",
            headers=ANY,
        )

    def test_save_property_listing_for_buying(self):
        # arrange
        self._set_config()
        sqlite = SQLite()

        # act
        global PROPERTIES
        for i in range(len(PROPERTIES)):
            PROPERTIES[i] = sqlite.save_property(PROPERTIES[i])

        # assert
        for property in PROPERTIES:
            loaded_property = sqlite.load_property(property.property_id)
            assert property.property_id == loaded_property.property_id

    def test_get_property_listing_for_renting(self, mocker):
        # arrange
        mocker.patch(
            "core.data_source_wrapper.request",
            TestRealestate._mock_realestate_rent_property_search_requests_get,
        )
        spy_request = mocker.spy(core.data_source_wrapper, "request")
        real_estate = RealEstateWrapper()

        # act
        global PROPERTIES
        PROPERTIES = real_estate.get_property_listing(
            ListingType.RENT,
            [PropertyType.HOUSE, PropertyType.TOWNHOUSE],
            3,
            400,
            None,
            City.ADELAIDE,
            State.SA,
            end_page=3,
            pause_range=(0, 0),
        )

        # assert
        spy_request.call_count = 3
        spy_request.assert_any_call(
            "GET",
            url="https://www.realestate.com.au/rent/property-house-townhouse-with-3-bedrooms-between-400-any-in-adelaide greater region,+sa/"
            "list-1?includeSurrounding=false&activeSort=price-asc&source=refinement",
            headers=ANY,
        )
        spy_request.assert_any_call(
            "GET",
            url="https://www.realestate.com.au/rent/property-house-townhouse-with-3-bedrooms-between-400-any-in-adelaide greater region,+sa/"
            "list-2?includeSurrounding=false&activeSort=price-asc&source=refinement",
            headers=ANY,
        )
        spy_request.assert_any_call(
            "GET",
            url="https://www.realestate.com.au/rent/property-house-townhouse-with-3-bedrooms-between-400-any-in-adelaide greater region,+sa/"
            "list-3?includeSurrounding=false&activeSort=price-asc&source=refinement",
            headers=ANY,
        )

    def test_save_property_listing_for_renting(self):
        # arrange
        self._set_config()
        sqlite = SQLite()

        # act
        global PROPERTIES
        for i in range(len(PROPERTIES)):
            PROPERTIES[i] = sqlite.save_property(PROPERTIES[i])

        # assert
        for property in PROPERTIES:
            loaded_property = sqlite.load_property(property.property_id)
            assert property.property_id == loaded_property.property_id

    def _set_config(self):
        config.CONFIG = config.Config(
            debug_mode=True,
            data_repository_type=DataRepositoryType.SQLITE,
            run_db_migrations=True,
            api_port=8080,
            api_reload=False,
            sqlite_connection_string="sqlite+pysqlite:///local/test.sqlite3",
            data_source_type=DataSourceType.REAL_ESTATE,
        )

    def _mock_realestate_buy_property_search_requests_get(method, url, headers):
        page: int
        if "list-" in url:
            page = url.split("list-")[1][0]
        with open(
            f"tests/data/realestate_buy_property_search_00{page}.html"
        ) as property_search_page:
            response = type(
                "requests.models.Response",
                (object,),
                dict(content=property_search_page.read(), status_code=200),
            )
            return response

    def _mock_realestate_rent_property_search_requests_get(method, url, headers):
        page: int
        if "list-" in url:
            page = url.split("list-")[1][0]
        with open(
            f"tests/data/realestate_rent_property_search_00{page}.html"
        ) as property_search_page:
            response = type(
                "requests.models.Response",
                (object,),
                dict(content=property_search_page.read(), status_code=200),
            )
            return response
