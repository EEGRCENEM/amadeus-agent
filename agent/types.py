from typing import Annotated, Literal

from pydantic import BaseModel, Field


IATACode = Annotated[
    str,
    Field(description="Unique IATA 3-letter airport code.", max_length=3, min_length=3),
]
ISOCountyCode = Annotated[
    str,
    Field(description="ISO 3166-1 2-letter country code.", max_length=2, min_length=2),
]
AirlineCode = Annotated[
    str,
    Field(description="Unique IATA 2-letter airline code.", max_length=2, min_length=2),
]

FlightNumber = Annotated[str, "The flight number as assigned by the carrier."]

TravelClass = Annotated[
    Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"], "Airline travel class."
]

ISODuration = Annotated[
    str, Field(description="Duration in ISO8601 PnYnMnDTnHnMnS format, e.g. PT2H10M.")
]
ISOLocalTime = Annotated[
    str,
    "Local date and time in ISO8601 YYYY-MM-ddThh:mm:ss format, e.g. 2017-02-10T20:40:00.",
]


class Timezone(BaseModel):
    offset: Annotated[
        str,
        Field(description="UTC Timezone offset. 00:00 means UTC time.", max_length=6),
    ]


class Coordinates(BaseModel):
    latitude: float
    longitude: float


Currency = Annotated[
    str,
    Field(description="ISO 4217 national currency code.", min_length=3, max_length=3),
]

AirportName = Annotated[str, "Name of airport."]
Municipality = Annotated[str, "Local municipality this location resides in."]


class Airport(BaseModel):
    name: AirportName
    iso_country: ISOCountyCode
    municipality: Municipality
    iata_code: IATACode
