""" Module for enumerations. """

from enum import StrEnum, auto


class DataRepositoryType(StrEnum):
    """Class for storing data repository type enumeration."""

    SQLITE = auto()


class DataSourceType(StrEnum):
    """Class for storing data source type enumeration."""

    REAL_ESTATE = auto()
    DOMAIN = auto()


class ListingType(StrEnum):
    """Class for storing listing type enumeration."""

    BUY = auto()
    RENT = auto()


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
    APARTMENT = auto()
    UNIT = auto()
    RETIREMENT_LIVING = auto()
    RESIDENTIAL_LAND = auto()
    BLOCK_OF_UNITS = auto()
    OTHER = auto()
