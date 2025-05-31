import pytest

from agent.tools import airport


def test_airports():
    assert airport.count_airports() > 100
    assert len(airport.find_airports_in_country("DK")) == 2
    assert airport.find_airport_by_iata_code("CPH").iso_country == "DK"
    assert airport.find_iata_code_for_airport("Billund") == "BLL"
