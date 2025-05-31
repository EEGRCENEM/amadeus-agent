from agent.tools import airport


def test_airports():
    assert airport.count_airports() > 100


def test_find_airports_in_country():
    assert len(airport.find_airports_in_country("CH")) == 2


def test_find_airports_by_iata():
    zrh_airport = airport.find_airport_by_iata_code("ZRH")
    assert zrh_airport is not None
    assert zrh_airport.iso_country == "CH"


def test_find_iata_for_airport():
    assert airport.find_iata_code_for_airport("Geneva") == "GVA"
