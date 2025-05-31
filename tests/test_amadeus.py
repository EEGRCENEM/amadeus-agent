import pytest

from agent.services.amadeus import FlightOffer
from agent.tools import amadeus
from agent.utils import camel_to_snake_key_recursive


@pytest.mark.skip("Disabled to reduce API usage.")
def _test_amadeus():
    response = amadeus.list_airline_destinations("LX")
    response = amadeus.list_direct_destinations("ZRH")


@pytest.mark.skip()
def test_amadeus():
    # Broken
    # response = amadeus.list_cheapest_flight_dates("NYC", "MAD")
    response = amadeus.list_cheapest_flights_for_journey()
    breakpoint()
