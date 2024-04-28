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
                        "Cookie": "reauid=c9b42e1735503100b91677678b030000797a5300; Country=AU; KFC=lkzIoe5u/ipUoxkNnEEkirOQVbpxiG8CHcoSqaqEZLA=; KP_UIDz-ssn=0azawzpF1n0FtB4uUSFuZUUEWBtgzahEX3qNgPjeiGGwx5BtQiP3iaT9zjDCMJZFXJql3WIHpmxA4VVKBvyehkAJ0bnjClC00zVMBcGBofmfGHjXIrcrBdIFhTRxMIOZadMRxKIUvCDK4eWUroNgdnbLZdFGP8jQfkqf8EfaSL7; KP_UIDz=0azawzpF1n0FtB4uUSFuZUUEWBtgzahEX3qNgPjeiGGwx5BtQiP3iaT9zjDCMJZFXJql3WIHpmxA4VVKBvyehkAJ0bnjClC00zVMBcGBofmfGHjXIrcrBdIFhTRxMIOZadMRxKIUvCDK4eWUroNgdnbLZdFGP8jQfkqf8EfaSL7; split_audience=e; _sp_ses.2fe7=*; _sp_id.2fe7=9bb65a38-d852-4f88-9bb7-42ac53ffe0e4.1735857851.1.1735857851.1735857851.7c6b59c3-58f7-419b-bb6f-af978f60bf65; VT_LANG=language%3Den-AU; mid=8547727610745379780; s_ecid=MCMID%7C45031464544863032442586225685345774297; AMCVS_341225BE55BBF7E17F000101%40AdobeOrg=1; utag_main=v_id:01942930c90f000d0474d77944d305075001e06d00bd0$_sn:1$_se:1$_ss:1$_st:1735859650640$ses_id:1735857850640%3Bexp-session$_pn:1%3Bexp-session$vapi_domain:realestate.com.au$dc_visit:1$dc_event:1%3Bexp-session$dc_region:ap-southeast-2%3Bexp-session$_prevpage:rea%3Ahomepage%3Bexp-1735861450992; s_nr30=1735857850993-New; _fbp=fb.2.1735857850999.749767172338253935; s_cc=true; nol_fpid=z660kmualle2ygxfrluv41cohkkot1735857851|1735857851101|1735857851101|1735857851101; DM_SitId1464=1; DM_SitId1464SecId12707=1; _gid=GA1.3.1612298235.1735857851; _gat_gtag_UA_143679184_2=1; _gcl_au=1.1.457155591.1735857852; _lr_geo_location_state=VIC; _lr_geo_location=AU; _ga_3J0XCBB972=GS1.1.1735857851.1.0.1735857851.0.0.0; _ga=GA1.1.564815369.1735857851; _ga_F962Q8PWJ0=GS1.1.1735857851.1.0.1735857851.0.0.0; AMCV_341225BE55BBF7E17F000101%40AdobeOrg=179643557%7CMCIDTS%7C20091%7CMCMID%7C45031464544863032442586225685345774297%7CMCAID%7CNONE%7CMCOPTOUT-1735865051s%7CNONE%7CMCAAMLH-1736462651%7C8%7CMCAAMB-1736462651%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCSYNCSOP%7C411-20098%7CvVersion%7C5.5.0; QSI_HistorySession=https%3A%2F%2Fwww.realestate.com.au%2F~1735857852462",
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
            case City.BALLARAT:
                return [
                    "ballarat central",
                    "ballarat east",
                    "ballarat north",
                    "ballarat - greater region",
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
