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
        "&activeSort=price-{sort_order_by_price}&source=refinement"
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
        pause_range: tuple[int, int] = (1, 5),
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
                    "region": region,
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
                        "Sec-Ch-Ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
                        "Sec-Ch-Ua-Mobile": "?0",
                        "Sec-Ch-Ua-Platform": '"macOS"',
                        "Sec-Fetch-Dest": "document",
                        "Sec-Fetch-Mode": "navigate",
                        "Sec-Fetch-Site": "same-origin",
                        "Sec-Fetch-User": "?1",
                        "Upgrade-Insecure-Requests": "1",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
                        "Cookie": "reauid=3c4ddc17554600004006af669603000048301700; Country=AU; KP_UIDz-ssn=08k3KAsyYpCCdJeMAzu3zxznTplxH9TRvc9C7YWtLQ8PlIFZkTCZy4T0V90ZOSbvcON0QrcFWOUXiphGJZRcDoQkg8jT5ynxjJzrPsinTMEVjhVo28hv7JeocWcgnRTc6ravzxPnLNCpoRn41OkpTx0EUvTnQx06JMH8UeTaPVidEaEbnWyRWbM5iXKbBUnupVljAzaXcu; KP_UIDz=08k3KAsyYpCCdJeMAzu3zxznTplxH9TRvc9C7YWtLQ8PlIFZkTCZy4T0V90ZOSbvcON0QrcFWOUXiphGJZRcDoQkg8jT5ynxjJzrPsinTMEVjhVo28hv7JeocWcgnRTc6ravzxPnLNCpoRn41OkpTx0EUvTnQx06JMH8UeTaPVidEaEbnWyRWbM5iXKbBUnupVljAzaXcu; KFC=kilAT6/WE0y7cLtGcdA/TUoxDTfeeyUFeYJdkP/VpC4=; split_audience=e; _sp_ses.2fe7=*; _sp_id.2fe7=2154819d-28b7-4f72-9ac2-1481608e6a3e.1722746440.1.1722746440.1722746440.049e17ba-8f17-483c-9333-6c7c2f5a60c9; VT_LANG=language%3Den-AU; mid=235846433634478637; _fbp=fb.2.1722746440316.556282242649907071; DM_SitId1464=1; DM_SitId1464SecId12707=1; s_ecid=MCMID%7C55710458737062899330330068900249590463; AMCVS_341225BE55BBF7E17F000101%40AdobeOrg=1; utag_main=v_id:01911bb0874200001d0cf0b408eb05075001e06d009dc$_sn:1$_se:1$_ss:1$_st:1722748239490$ses_id:1722746439490%3Bexp-session$_pn:1%3Bexp-session$vapi_domain:realestate.com.au$dc_visit:1$dc_event:1%3Bexp-session$dc_region:ap-southeast-2%3Bexp-session$_prevpage:rea%3Ahomepage%3Bexp-1722750040462; s_nr30=1722746440463-New; s_cc=true; nol_fpid=ix3lzo4ooqfmwzp6rajuu8fbmiu011722746440|1722746440663|1722746440663|1722746440663; _lr_geo_location_state=VIC; _lr_geo_location=AU; _gid=GA1.3.220213104.1722746441; _gat_gtag_UA_143679184_2=1; _gcl_au=1.1.1628438401.1722746441; _ga_3J0XCBB972=GS1.1.1722746440.1.0.1722746440.0.0.0; _ga=GA1.1.718688407.1722746441; _ga_F962Q8PWJ0=GS1.1.1722746440.1.0.1722746440.0.0.0; AMCV_341225BE55BBF7E17F000101%40AdobeOrg=-330454231%7CMCIDTS%7C19940%7CMCMID%7C55710458737062899330330068900249590463%7CMCAID%7CNONE%7CMCOPTOUT-1722753640s%7CNONE%7CMCAAMLH-1723351240%7C8%7CMCAAMB-1723351240%7Cj8Odv6LonN4r3an7LhD3WZrU1bUpAkFkkiY1ncBR96t2PTI%7CMCSYNCSOP%7C411-19947%7CvVersion%7C3.1.2; QSI_HistorySession=https%3A%2F%2Fwww.realestate.com.au%2F~1722746442381",
                    },
                )
                soup = BeautifulSoup(response.content, features="html.parser")
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
