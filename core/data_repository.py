""" Module for data repository. """

from abc import ABC
from datetime import datetime
from typing import Annotated, List, Optional, Self
from uuid import UUID, uuid4

from annotated_types import Ge, Gt
from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    ValidationError,
    model_validator,
)
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Mapped, Session, declarative_base, exc, mapped_column
from sqlalchemy.types import DateTime, Enum, Float, Integer, SmallInteger, Unicode, Uuid
from structlog import get_logger

from core import config
from core.config import DataSourceType
from core.data_source import PropertyType
from core.lib import now_utc
from core.sql_migrations import run

Base = declarative_base()


class Property(Base):
    """Class for property table."""

    __tablename__ = "property"

    # primary and foreign keys
    property_id: Mapped[UUID] = mapped_column(Uuid(), default=uuid4, primary_key=True)

    # core fields
    data_source_type: Mapped[DataSourceType] = mapped_column(Enum(DataSourceType))
    query_region: Mapped[str] = mapped_column(Unicode(200))
    url: Mapped[str] = mapped_column(Unicode(250))
    price_detail: Mapped[str] = mapped_column(Unicode(100))
    address: Mapped[str] = mapped_column(Unicode(200))
    num_bedrooms: Mapped[Optional[int]] = mapped_column(SmallInteger())
    num_bathrooms: Mapped[Optional[int]] = mapped_column(SmallInteger())
    num_carparks: Mapped[Optional[int]] = mapped_column(SmallInteger())
    area_sqm: Mapped[Optional[int]] = mapped_column(Integer())
    property_type: Mapped[PropertyType] = mapped_column(Enum(PropertyType))
    remarks: Mapped[str] = mapped_column(Unicode(200))

    # time and duration fields
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime())
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime())
    scrape_duration_seconds: Mapped[Optional[float]] = mapped_column(Float())
    total_duration_seconds: Mapped[Optional[float]] = mapped_column(Float())
    first_created: Mapped[datetime] = mapped_column(DateTime(), default=now_utc)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(), default=now_utc, onupdate=now_utc
    )

    @classmethod
    def get_exclude_fields_for_logging(cls) -> set[str]:
        exclude_fields = (
            "num_bedrooms",
            "num_bathrooms",
            "num_carparks",
            "area_sqm",
            "remarks",
        )
        return exclude_fields


def _validate_time_fields(self):
    if self.end_time and self.start_time:
        assert self.end_time > self.start_time, "end time is less than start time"
    if self.start_time and self.first_created:
        assert (
            self.start_time > self.first_created
        ), "start time is less than first created time"
    if self.end_time and self.first_created:
        assert (
            self.end_time > self.first_created
        ), "end time is less than first created time"
    if self.total_duration_seconds and self.scrape_duration_seconds:
        assert (
            self.total_duration_seconds > self.scrape_duration_seconds
        ), "total duration seconds is less than scrape duration seconds"
    if self.end_time and self.start_time and self.total_duration_seconds:
        assert (
            self.end_time - self.start_time
        ).total_seconds != self.total_duration_seconds, "difference between end time and start time is not equal to total duration seconds"
    if self.last_updated and self.first_created:
        assert (
            self.last_updated > self.first_created
        ), "last updated is less than first created"


class PropertyModel(BaseModel):
    """Class for property model."""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    # primary and foreign keys
    property_id: UUID

    # core fields
    data_source_type: DataSourceType
    query_region: Annotated[
        str, StringConstraints(max_length=Property.query_region.type.length)
    ]
    url: Annotated[str, StringConstraints(max_length=Property.url.type.length)]
    price_detail: Mapped[str] = Annotated[
        str, StringConstraints(max_length=Property.price_detail.type.length)
    ]
    address: Mapped[str] = Annotated[
        str, StringConstraints(max_length=Property.address.type.length)
    ]
    num_bedrooms: Annotated[int, Ge(1)] | None
    num_bathrooms: Annotated[int, Ge(0)] | None
    num_carparks: Annotated[int, Ge(0)] | None
    area_sqm: Annotated[int, Gt(0)] | None
    property_type: PropertyType
    remarks: Mapped[str] = (
        Annotated[str, StringConstraints(max_length=Property.remarks.type.length)]
        | None
    )

    # time and duration fields
    start_time: datetime | None
    end_time: datetime | None
    scrape_duration_seconds: Annotated[float, Gt(0)] | None
    total_duration_seconds: Annotated[float, Gt(0)] | None
    first_created: datetime
    last_updated: datetime

    @model_validator(mode="after")
    def check_time_and_duration(self) -> Self:
        _validate_time_fields(self)
        return self

    @classmethod
    def get_exclude_fields_for_logging() -> set[str]:
        exclude_fields = (
            "num_bedrooms",
            "num_bathrooms",
            "num_carparks",
            "area_sqm",
            "remarks",
        )
        return exclude_fields


class DataRepository(ABC):
    """Class for data repository."""

    engine: Engine = None

    def __init__(self, connection_string: str, echo: bool, run_sql_migrations: bool):
        if run_sql_migrations:
            run.run_sql_migrations(connection_string)
        self.engine = create_engine(connection_string, echo=echo)

    def save_property(self, property: Property):
        """Save property in data repository."""

        logger = get_logger().bind(
            job=(
                {
                    k: str(v)
                    for k, v in property.__dict__.items()
                    if k not in Property.get_exclude_fields_for_logging()
                }
                if property
                else None
            )
        )
        logger.info("Starting save property")

        with Session(self.engine) as session:
            session.add(property)
            session.flush()
            try:
                PropertyModel.model_validate(property)
            except ValidationError as error:
                logger.error(
                    error,
                    stack_info=config.CONFIG.debug_mode,
                    exc_info=config.CONFIG.debug_mode,
                )
                raise error
            session.commit()
            session.refresh(property)

        logger.info("Completed save job")

    def load_property(self, property_id: UUID) -> Property:
        """Load property from data repository."""

        logger = get_logger().bind(property_id=str(property_id))
        logger.info("Starting load property")

        with Session(self.engine) as session:
            try:
                job = session.get_one(Property, {"property_id": property_id})
                logger.info("Completed load property")
                return job
            except exc.NoResultFound as error:
                logger.error(
                    error,
                    stack_info=config.CONFIG.debug_mode,
                    exc_info=config.CONFIG.debug_mode,
                )
                raise error
