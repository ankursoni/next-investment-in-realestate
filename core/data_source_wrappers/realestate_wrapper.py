""" Module for realestate.com.au wrapper. """

import random
import time
from typing import List

from bs4 import BeautifulSoup
from structlog import get_logger

from core import lib
from core.data_repository import Property
from core.data_source_wrapper import DataSourceWrapper
from core.enum import City, DataSourceType, ListingType, PropertyType, State


class RealEstateWrapper(DataSourceWrapper):
    """Class for realestate.com.au wrapper."""

    domain_url = "https://www.realestate.com.au"
    property_listing_url_template = (
        f"{domain_url}/{{listing_type}}/property-{{property_types}}-with-{{min_bedrooms}}-bedrooms-between-"
        "{min_price}-{max_price}-in-{region},+{state}/list-{page}?includeSurrounding={include_surrounding}"
        "&activeSort=price-{sort_order_by_price}"
    )

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
        pause_range: tuple[int, int] = (3, 5),
    ) -> List[Property]:
        """Function to get property listing."""

        logger = get_logger().bind(
            listing_type=listing_type,
            property_types=property_types,
            min_bedrooms=min_bedrooms,
            min_price=min_price,
            max_price=max_price,
            city=city,
            state=state,
            include_surrounding=include_surrounding,
            sort_order_by_price=sort_order_by_price,
            start_page=start_page,
            end_page=end_page,
            pause_range=pause_range,
        )
        logger.info("Starting get property listing")

        result = []
        regions = self._get_regions_from_city(city)
        for region in regions:
            for page in range(start_page, end_page + 1):
                start_time = lib.now_utc()
                url_template_values = {
                    "listing_type": listing_type,
                    "property_types": "-".join(property_types),
                    "min_bedrooms": min_bedrooms if min_bedrooms else "any",
                    "min_price": min_price if min_price else "any",
                    "max_price": max_price if max_price else "any",
                    "region": region.replace(" ", "+"),
                    "state": state,
                    "page": page,
                    "include_surrounding": str(include_surrounding).lower(),
                    "sort_order_by_price": sort_order_by_price,
                }
                request_url = self.property_listing_url_template.format(
                    **url_template_values
                )
                response = self._make_web_request(
                    request_url,
                    headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                        "Accept-Encoding": "gzip, deflate, br, zstd",
                        "Accept-Language": "en-AU,en;q=0.9",
                        "Cache-Control": "max-age=0",
                        "Priority": "u=0, i",
                        "Referer": "https://www.realestate.com.au/",
                        "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"macOS"',
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Fetch-User": "?1",
                        "Upgrade-Insecure-Requests": "1",
                        "Requests": "",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                        "Cookie": "reauid=375ad617b37420008164696770000000a2c50100; Country=AU; KFC=5nooVbu3ifFOalHmHQa3NIoPOU2UN+Wn0ShUFBW1DKY=; KP_UIDz-ssn=021cJKhi9KjpIlhNBV5tpxVnCptSR6dlTAHOzKXySRqZoJX7GxgEUMbitN00sgzbY1MtJevF44SA6hJA7OxgLXvd14ds6kjSqhwIIEjJH7p92smpHiZ0SMn1aDZxPOu2zJ7ZO2Op5m2RC96rFvudlOzNpzEpJDFZ14z8kcFcU1uMIRClxRcLg2cIxLOStLMf0Oc4vPiVoptk4; KP_UIDz=021cJKhi9KjpIlhNBV5tpxVnCptSR6dlTAHOzKXySRqZoJX7GxgEUMbitN00sgzbY1MtJevF44SA6hJA7OxgLXvd14ds6kjSqhwIIEjJH7p92smpHiZ0SMn1aDZxPOu2zJ7ZO2Op5m2RC96rFvudlOzNpzEpJDFZ14z8kcFcU1uMIRClxRcLg2cIxLOStLMf0Oc4vPiVoptk4; split_audience=d; _sp_ses.2fe7=*; _sp_id.2fe7=05bc7164-6eed-446b-be52-6624d0831828.1734960258.1.1734960258.1734960258.7a9bb5ad-b201-49e4-986d-0475e2a94c08; VT_LANG=language%3Den-AU; mid=15607952395345856674; _fbp=fb.2.1734960258111.925861282917545804; s_ecid=MCMID%7C02994068841750385760013424404832331385; AMCVS_341225BE55BBF7E17F000101%40AdobeOrg=1; utag_main=v_id:0193f3b09b45000939114962dab605075001e06d009dc$_sn:1$_se:1$_ss:1$_st:1734962057862$ses_id:1734960257862%3Bexp-session$_pn:1%3Bexp-session$vapi_domain:realestate.com.au$dc_visit:1$dc_event:1%3Bexp-session$dc_region:ap-southeast-2%3Bexp-session$_prevpage:rea%3Ahomepage%3Bexp-1734963858283; s_nr30=1734960258284-New; nol_fpid=3uyrwjyboy5fiot7fvcpqrymr40zp1734960258|1734960258391|1734960258391|1734960258391; s_cc=true; DM_SitId1464=1; DM_SitId1464SecId12707=1; _lr_geo_location_state=VIC; _lr_geo_location=AU; _gid=GA1.3.2040437228.1734960259; _gat_gtag_UA_143679184_2=1; _ga_F962Q8PWJ0=GS1.1.1734960258.1.0.1734960258.0.0.0; _ga=GA1.1.319168302.1734960259; _gcl_au=1.1.1136846169.1734960259; AMCV_341225BE55BBF7E17F000101%40AdobeOrg=179643557%7CMCIDTS%7C20081%7CMCMID%7C02994068841750385760013424404832331385%7CMCAID%7CNONE%7CMCOPTOUT-1734967458s%7CNONE%7CMCAAMLH-1735565058%7C8%7CMCAAMB-1735565058%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCSYNCSOP%7C411-20088%7CvVersion%7C5.5.0; _ga_3J0XCBB972=GS1.1.1734960258.1.0.1734960258.0.0.0; QSI_HistorySession=https%3A%2F%2Fwww.realestate.com.au%2F~1734960259790",
                    },
                )
                # response_data = brotli.decompress(response.content) if response.headers.get('Content-Encoding') == 'br' else response.content
                response_data = response.content
                soup = BeautifulSoup(response_data, features="html.parser")
                property_cards = soup.find_all(class_="residential-card__content")
                for index, property_card in enumerate(property_cards):
                    logger.debug("Starting parse of property listing card", index=index)
                    price_card = property_card.find(class_="property-price")
                    price = price_card.text if price_card else self.NOT_AVAILABLE
                    address_card = property_card.find(
                        class_="details-link residential-card__details-link"
                    )
                    url = (
                        (self.domain_url + address_card.attrs["href"])
                        if address_card and hasattr(address_card, "href")
                        else self.NOT_AVAILABLE
                    )
                    address = address_card.text

                    icon_card = property_card.find(class_="piped-content")
                    aria_labels = icon_card.find_all(
                        class_="View__PropertyDetail-sc-11ysrk6-0"
                    )
                    aria_labels.append(
                        icon_card.find(class_="View__PropertySize-sc-1psmy31-0")
                    )
                    aria_labels.append(
                        icon_card.find(class_="residential-card__property-type")
                    )

                    label_bedrooms = [
                        label.attrs["aria-label"]
                        for label in aria_labels
                        if label and "bedroom" in label.attrs["aria-label"]
                    ]
                    num_bedrooms = (
                        int(lib.keep_only_numbers(label_bedrooms[0]).strip())
                        if len(label_bedrooms) == 1
                        else None
                    )

                    label_bathrooms = [
                        label.attrs["aria-label"]
                        for label in aria_labels
                        if label and "bathroom" in label.attrs["aria-label"]
                    ]
                    num_bathrooms = (
                        int(lib.keep_only_numbers(label_bathrooms[0]).strip())
                        if len(label_bathrooms) == 1
                        else None
                    )

                    label_carparks = [
                        label.attrs["aria-label"]
                        for label in aria_labels
                        if label and "parking space" in label.attrs["aria-label"]
                    ]
                    num_carparks = (
                        int(lib.keep_only_numbers(label_carparks[0]).strip())
                        if len(label_carparks) == 1
                        else None
                    )

                    label_area = [
                        label.attrs["aria-label"]
                        for label in aria_labels
                        if label and "land size" in label.attrs["aria-label"]
                    ]
                    area_sqm = (
                        int(lib.keep_only_numbers(label_area[0]).strip())
                        if len(label_area) == 1
                        else None
                    )

                    label_property_type = [
                        label.attrs["aria-label"]
                        for label in aria_labels
                        if label and "property type" in label.attrs["aria-label"]
                    ]
                    property_type = (
                        lib.parse_strenum_from_string(
                            PropertyType,
                            label_property_type[0].replace(" property type", ""),
                        )
                        if len(label_property_type) == 1
                        else None
                    )

                    end_time = lib.now_utc()
                    result.append(
                        Property(
                            data_source_type=DataSourceType.REAL_ESTATE,
                            listing_type=listing_type,
                            query_city=city.upper() if city else city,
                            query_state=state.upper() if state else state,
                            query_region=region.upper() if region else region,
                            search_page=page,
                            url=url,
                            price_detail=price,
                            address=address,
                            num_bedrooms=num_bedrooms,
                            num_bathrooms=num_bathrooms,
                            num_carparks=num_carparks,
                            area_sqm=area_sqm,
                            property_type=(
                                property_type if property_type else PropertyType.OTHER
                            ),
                            start_time=start_time,
                            end_time=end_time,
                            total_duration_seconds=(
                                end_time - start_time
                            ).total_seconds(),
                        )
                    )
                is_last_page: bool
                if len(property_cards) > 0:
                    counts_summary = soup.find(
                        class_="View__ResultsSummaryText-sc-ongnsj-0"
                    )
                    counts_summary_text = (
                        counts_summary.attrs["aria-label"]
                        if hasattr(counts_summary, "aria-label")
                        else None
                    )
                    split = counts_summary_text.split(" of ")
                    if len(split) == 1:
                        is_last_page = True
                    else:
                        total_count = split[1].replace(" properties", "")
                        is_last_page = split[0].endswith(f"to {total_count}")
                else:
                    is_last_page = True
                time.sleep(random.uniform(*pause_range))
                if is_last_page:
                    break

        logger.info("Completed get property listing")
        return result

    def _get_regions_from_city(self, city: City) -> List[str]:
        match city:
            case City.ADELAIDE:
                return ["adelaide greater region"]
            case City.BRISBANE:
                return [
                    "brisbane - greater region",
                    "brisbane - northern region",
                    "brisbane - southern region",
                    "brisbane - western region",
                    "brisbane - eastern region",
                    "brisbane - inner city region",
                ]
            case City.MELBOURNE:
                return [
                    "melbourne - northern region",
                    "western melbourne",
                    "south east melbourne",
                    "eastern melbourne",
                    "inner east melbourne",
                    "melbourne city - greater region",
                ]
            case City.PERTH:
                return [
                    "perth - greater region",
                    "perth - cbd and inner suburbs",
                ]
            case City.SYDNEY:
                return [
                    "hunter region",
                    "north coast",
                    "south coast",
                    "western sydney",
                    "south western sydney",
                    "inner west",
                    "eastern suburbs",
                ]
