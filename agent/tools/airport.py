import contextlib

import fastmcp

from agent.services.airport import Airport, AirportService
from agent.types import IATACode, ISOCountyCode


@contextlib.contextmanager
def airport_service():
    yield AirportService()


def list_airports() -> list[Airport]:
    """Get a list of all airports.

    Returns:
        A list of Airport objects.
    """
    with airport_service() as service:
        return list(service.list_airports())


def count_airports() -> int:
    """Get the number of airports available.

    Returns:
        The number of airports.
    """
    with airport_service() as service:
        return service.count_airports()


def find_iata_code_for_airport(search_term: str) -> IATACode | None:
    """Given a search term, find the IATA code for the airport that includes search_term as substring.

    Args:
        search_term: Search term for name (case sensitive).

    Returns:
        The IATA code matching search_term if any else None.
    """
    with airport_service() as service:
        return service.find_iata_code_for_airport(search_term)


def find_airport_by_iata_code(iata_code: IATACode) -> Airport | None:
    """Given an IATACode find the corresponding airport.

    Args:
        iata_code: The IATA code to search for.

    Returns:
        Airport if matches else None.
    """
    with airport_service() as service:
        return service.find_airport_by_iata_code(iata_code)


def find_airports_in_country(iso_country: ISOCountyCode) -> list[Airport]:
    """Given a country code find all airports in that country.

    Args:
        iso_country: ISO country code to search with.

    Returns:
        All airports in the country. Can be empty list if nothing found.
    """
    with airport_service() as service:
        return list(service.find_airports_in_country(iso_country))


def add_tools(mcp: fastmcp.FastMCP):
    mcp.add_tool(list_airports)
    mcp.add_tool(count_airports)
    mcp.add_tool(find_iata_code_for_airport)
    mcp.add_tool(find_airport_by_iata_code)
    mcp.add_tool(find_airports_in_country)
