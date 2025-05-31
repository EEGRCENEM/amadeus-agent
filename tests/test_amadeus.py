import pytest

from agent.tools import amadeus
from agent.services.amadeus import Passengers


@pytest.mark.skip("Disabled to reduce API usage.")
def test_list_airline_destinations():
    result = amadeus.list_airline_destinations("LX")
    assert len(result.root) > 0


@pytest.mark.skip("Disabled to reduce API usage.")
def test_list_direct_destinations():
    result = amadeus.list_direct_destinations("ZRH")
    assert len(result.root) > 0


@pytest.mark.skip("Disabled to reduce API usage.")
def test_list_cheapest_flights():
    response = amadeus.list_cheapest_flights_for_journey(
        origin="ZRH",
        destination="MAD",
        date="2025-10-04",
        passengers=Passengers(adults=2),
        non_stop=True,
    )
    assert len(response.root) > 0

