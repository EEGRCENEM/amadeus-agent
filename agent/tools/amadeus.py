import contextlib

import fastmcp

from agent.services.amadeus import AmadeusService, DestinationsRoot, FlightOffersRoot
from agent.types import AirlineCode, IATACode

# Keep a global instance to prevent having to reinstantiate.
_instance = AmadeusService()


@contextlib.contextmanager
def amadeus_service():
    yield _instance


def list_direct_destinations(origin: IATACode) -> DestinationsRoot:
    """Get all direct flight destinations from a given departure airport.

    Args:
        origin: Departure airport IATA code.

    Returns:
        DestinationsRoot describing all destinations.
    """
    with amadeus_service() as service:
        return service.list_direct_destinations(origin=origin)


def list_airline_destinations(airline: AirlineCode) -> DestinationsRoot:
    """Get all destinations for a given airline.

    Args:
        airline: Airline code.

    Returns:
        DestinationsRoot describing all destinations.
    """
    with amadeus_service() as service:
        return service.list_airline_destinations(airline=airline)


def get_flight_order(order_id: str):
    """Get the flight order details for an order ID.

    Args:
        order_id: Unique flight order identitifer.

    Returns:
        Unknown.
    """
    with amadeus_service() as service:
        return service.get_flight_order(order_id=order_id)


def list_cheapest_flight_dates(origin: IATACode, destination: IATACode):
    """Find the cheapest flight dates from an origin to a destination.

    Args:
        origin: The city/airport IATA code from which the flight will depart. "NYC", for example for New-York.
        destination: The city/airport IATA code to which the flight is going. "MAD", for example for Madrid.

    Returns:
        Unknown.
    """
    with amadeus_service() as service:
        return service.list_cheapest_flight_dates(
            origin=origin, destination=destination
        )


def list_cheapest_flights_for_journey(
    origin: IATACode, destination: IATACode, date: str, adults: int
) -> FlightOffersRoot:
    """Get the cheapest flights on a given journey.

    Args:
        origin: The city/airport IATA code from which the flight will depart.
        destination: The city/airport IATA code to which the flight is going.
        date: The date on which to fly out, in `YYYY-MM-DD` format.
        adults: The number of adult passengers with age 12 or older.

    Returns:
        FlightOffersRoot describing all cheapest journies for criteria.
    """
    with amadeus_service() as service:
        return service.list_cheapest_flights_for_journey(
            origin=origin,
            destination=destination,
            departure_date=date,
            return_date=None,
            adults=adults,
            # Custom params
            travel_class="ECONOMY",
            non_stop=True,
            currency="CHF",
        )


def add_tools(mcp: fastmcp.FastMCP):
    mcp.add_tool(list_direct_destinations)
    mcp.add_tool(list_airline_destinations)
    # mcp.add_tool(get_flight_order)
    # mcp.add_tool(list_cheapest_flight_dates)
    mcp.add_tool(list_cheapest_flights_for_journey)
