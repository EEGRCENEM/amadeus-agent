from __future__ import annotations
import os
from typing import Annotated, Any, Literal

from amadeus import Client, Response
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



class Passengers(BaseModel):
    adults: int
    children: int | None = None
    infants: int | None = None


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


class AmadeusService(Client):
    def __init__(self):
        super().__init__(
            hostname=os.environ.get("AMADEUS_ENV"),
            client_id=os.environ.get("AMADEUS_KEY"),
            client_secret=os.environ.get("AMADEUS_SECRET"),
        )

    def request(
        self, verb: Literal["GET", "POST", "DELETE"], path: str, params: dict[str, Any]
    ) -> Response:
        """Override service requests with custom logic."""

        def convert_value(value: Any) -> Any:
            # API expects booleans as JSON-compatible strings.
            if value in (True, False):
                return str(value).lower()
            return value

        params = {
            key: convert_value(value)
            for key, value in params.items()
            if value is not None
        }

        response = super().request(verb=verb, path=path, params=params)
        response.data = camel_to_snake_key_recursive(response.data)

        return response

    def list_direct_destinations(self, origin: IATACode) -> DestinationsRoot:
        response = self.airport.direct_destinations.get(departureAirportCode=origin)
        return DestinationsRoot.model_validate({"root": response.data})

    def list_airline_destinations(self, airline: AirlineCode) -> DestinationsRoot:
        response = self.airline.destinations.get(airlineCode=airline)
        return DestinationsRoot.model_validate({"root": response.data})

    def get_flight_order(self, order_id: str):
        return (self.booking.flight_order(order_id).get()).data

    def list_cheapest_flight_dates(self, origin: IATACode, destination: IATACode):
        return self.shopping.flight_dates.get(
            origin=origin, destination=destination
        ).data

    def list_cheapest_flights_for_journey(
        self,
        *,
        origin: IATACode,
        destination: IATACode,
        departure_date: ISOLocalTime,
        return_date: ISOLocalTime | None,
        passengers: Passengers,
        travel_class: TravelClass | None = None,
        included_airline_codes: tuple[AirlineCode, ...] | None = None,
        non_stop: bool = False,
        currency: Currency | None = None,
        max_price: int | None = None,
    ) -> FlightOffersRoot:
        response = self.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            returnDate=return_date,
            adults=passengers.adults,
            children=passengers.children,
            infants=passengers.infants,
            travelClass=travel_class,
            currencyCode=currency or os.environ.get("AMADEUS_CURRENCY"),
            includedAirlineCodes=",".join(included_airline_codes)
            if included_airline_codes
            else None,
            nonStop=non_stop,
            maxPrice=max_price,
        )

        return FlightOffersRoot.model_validate({"root": response.data})
