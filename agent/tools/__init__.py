import fastmcp

from agent.tools import amadeus
from agent.tools import airport


def add_tools(mcp: fastmcp.FastMCP):
    airport.add_tools(mcp)
    amadeus.add_tools(mcp)
