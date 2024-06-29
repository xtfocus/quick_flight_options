import json
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Optional

from pkg_resources import resource_filename
from pydantic import BaseModel, Field, ValidationInfo, field_validator

with open(resource_filename("flyfare", "data/airports.json")) as fid:
    SOUTHEAST_ASIA_AIRPORTS = json.load(fid)

# with open("airports.json") as f:
#    SOUTHEAST_ASIA_AIRPORTS = json.load(f)


class DepartureDate(BaseModel):
    """
    Pydantic model for departure date validation.

    start_date must be >= tomorrow
    end_date either None or >= start_date
    """

    start_date: date = Field(...)
    end_date: date = Field(None)

    @field_validator("start_date")
    def validate_start_date(cls, value: date) -> date:
        tomorrow = date.today() + timedelta(days=1)
        if value < tomorrow:
            raise ValueError(f"Start date must be at least {tomorrow}.")
        return value

    @field_validator("end_date")
    def validate_end_date(cls, value: date, info: ValidationInfo) -> date:
        start_date = info.data.get("start_date")
        if value is not None and start_date is not None:
            if value < start_date:
                raise ValueError(
                    "End date must be greater than or equal to the start date."
                )
        return value


class AirportCode(BaseModel):
    airport_code: str = Field(description="Airport Code")

    @field_validator("airport_code")
    def check_airport_code(cls, v):
        if v.upper() not in SOUTHEAST_ASIA_AIRPORTS:
            raise ValueError("Invalid airport code")
        return v


class CabinClass(str, Enum):
    economy = "economy"
    premiumeconomy = "premiumeconomy"
    business = "business"
    first = "first"


class FlightSearchOptions(BaseModel):
    from_airport: AirportCode = Field(description="Departure airport")
    to_airport: AirportCode = Field(description="Landing airport")
    departure_date: datetime
    return_date: Optional[datetime] = None
    adults: int = Field(..., gt=0, description="Number of adult passengers")
    children: int = Field(..., ge=0, description="Number of child passengers")
    cabin_class: CabinClass = Field(..., description="Cabin class for the flight")
    prefer_direct: bool = Field(..., description="Preference for direct flights")
