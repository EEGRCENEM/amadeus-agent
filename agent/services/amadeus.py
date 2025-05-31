from __future__ import annotations
import os
from datetime import datetime, timedelta
from typing import Annotated, Any, Literal

from amadeus import Client, Response
import dotenv
from pydantic import BaseModel, Field

from agent.types import (
    AirlineCode,
    Coordinates,
    Currency,
    FlightNumber,
    IATACode,
    ISODuration,
    ISOLocalTime,
    TravelClass,
)
from agent.utils import camel_to_snake_key_recursive

# TODO: Store this somewhere else
dotenv.load_dotenv()

HTTPMethod = Literal["GET", "POST", "DELETE"]


class Destination(BaseModel):
    type: Annotated[Literal["location"], "Destination type."]
    subtype: Annotated[Literal["city", "airport"], "Destination subtype."]
    name: Annotated[str, "Human readable name of destination."]
    geo_code: Annotated[Coordinates, "Geographical coordinates of destination."]


class DestinationsRoot(BaseModel):
    root: list[Destination]


class Flight(BaseModel):
    iata_code: IATACode
    at: ISOLocalTime


class FlightSegment(BaseModel):
    """Defining a flight segment; including both operating and marketing details when applicable."""

    departure: Flight
    arrival: Flight
    carrier_code: AirlineCode
    number: FlightNumber
    duration: ISODuration
    number_of_stops: int
    blacklisted_in_eu: Annotated[
        bool,
        "Whether service is banned in the EU. The list of the banned airlines is published in the Official Journal of the European Union, where they are included as annexes A and B to the Commission Regulation. The blacklist of an airline can concern all its flights or some specific aircraft types pertaining to the airline.",
    ]


class Itinerary(BaseModel):
    duration: ISODuration
    segments: list[FlightSegment]


class FeePricing(BaseModel):
    type: Literal["TICKETING", " FORM_OF_PAYMENT", "SUPPLIER"]
    amount: str


class Pricing(BaseModel):
    currency: Currency
    total: Annotated[str, "Total amount paid by the user."]
    base: Annotated[str, "Amount without taxes."]
    fees: Annotated[list[FeePricing] | None, "List of applicable fees."] = None
    grand_total: Annotated[
        str | None,
        "Total amount paid by the user (including fees and selected additional services).",
    ] = None


class PricingOptions(BaseModel):
    fare_type: list[Literal["PUBLISHED", "NEGOTIATED", "CORPORATE"]]
    included_checked_bags_only: Annotated[
        bool, "If true, returns the flight-offers with included checked bags only."
    ]
    refundable_fare: Annotated[
        bool | None, "If true, returns the flight-offers with refundable fares only."
    ] = None


class TravelerPricing(BaseModel):
    traveler_id: str
    fare_option: str
    traveler_type: Annotated[
        Literal[
            "ADULT",
            "CHILD",
            "SENIOR",
            "YOUNG",
            "HELD_INFANT",
            "SEATED_INFANT",
            "STUDENT",
        ],
        "Age restrictions : CHILD < 12y, HELD_INFANT < 2y, SEATED_INFANT < 2y, SENIOR >=60y",
    ]
    price: Pricing


class FlightOffer(BaseModel):
    type: Literal["flight-offer"]
    id: Annotated[str, "Internal ID to refer to this offer."]
    one_way: Annotated[
        bool,
        "If true, the flight offer can be combined with other oneWays flight-offers to complete the whole journey (one-Way combinable feature).",
    ]
    last_ticketing_date: Annotated[
        str,
        "If booked on the same day as the search (with respect to timezone), this flight offer is guaranteed to be thereafter valid for ticketing until this date/time (included). Unspecified when it does not make sense for this flight offer (e.g. no control over ticketing once booked). Information only this attribute is not used in input of pricing request. Local date and time in YYYY-MM-ddThh:mm:ss format, e.g. 2017-02-10T20:40:00.",
    ]
    number_of_bookable_seats: int = Field(
        description="Number of seats bookable in a single request.", le=9, gt=-1
    )
    itineraries: list[Itinerary]
    price: Pricing
    pricing_options: PricingOptions
    traveler_pricings: list[TravelerPricing]


class FlightOffersRoot(BaseModel):
    root: list[FlightOffer]


class APIThrottleException(Exception):
    """Raised when too many requests are called in a short amount of time."""


class NaiveRateLimiter:
    def __init__(self):
        self._last_request_time: datetime | None = None

    def __enter__(self) -> None:
        request_time = datetime.now()

        if self._last_request_time is not None and (
            request_time - self._last_request_time
        ) < timedelta(seconds=30):
            self._last_request_time = request_time
            raise APIThrottleException
        else:
            self._last_request_time = request_time

    def __exit__(self, *arg, **kwargs):
        return None


class AmadeusService(Client):
    def __init__(self):
        super().__init__(
            hostname="test",
            client_id=os.environ.get("AMADEUS_KEY"),
            client_secret=os.environ.get("AMADEUS_SECRET"),
        )
        self._rate_limiter = NaiveRateLimiter()

    def request(self, verb: HTTPMethod, path: str, params: dict[str, Any]) -> Response:
        """Override service requests to prevent sending too many requests."""
        params = {key: value for key, value in params.items() if value is not None}

        with self._rate_limiter:
            return super().request(verb=verb, path=path, params=params)

    def list_direct_destinations(self, origin: IATACode) -> DestinationsRoot:
        response = camel_to_snake_key_recursive(
            self.airport.direct_destinations.get(departureAirportCode=origin).data
        )
        return DestinationsRoot.model_validate({"root": response})

    def list_airline_destinations(self, airline: AirlineCode) -> DestinationsRoot:
        response = camel_to_snake_key_recursive(
            self.airline.destinations.get(airlineCode=airline).data
        )
        return DestinationsRoot.model_validate({"root": response})

    def get_flight_order(self, order_id: str):
        return camel_to_snake_key_recursive(self.booking.flight_order(order_id).get())

    def list_cheapest_flight_dates(self, origin: IATACode, destination: IATACode):
        return camel_to_snake_key_recursive(
            self.shopping.flight_dates.get(origin=origin, destination=destination).data
        )

    def list_cheapest_flights_for_journey(
        self,
        *,
        origin: IATACode,
        destination: IATACode,
        departure_date: ISOLocalTime,
        return_date: ISOLocalTime | None,
        adults: int,
        children: int | None = None,
        infants: int | None = None,
        travel_class: TravelClass | None = None,
        included_airline_codes: tuple[AirlineCode, ...] | None = None,
        non_stop: bool = False,
        currency: Currency | None = None,
        max_price: int | None = None,
    ) -> FlightOffersRoot:
        response = camel_to_snake_key_recursive(
            self.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                returnDate=return_date,
                adults=str(adults),
                children=str(children) if children else None,
                infants=str(infants) if infants else None,
                travelClass=travel_class,
                currencyCode=currency,
                includedAirlineCodes=",".join(included_airline_codes)
                if included_airline_codes
                else None,
                nonStop=non_stop,
                maxPrice=max_price,
            ).data
        )
        return FlightOffersRoot.model_validate({"root": response})
