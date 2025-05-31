import logging

from fastmcp import FastMCP

from agent.tools import add_tools


mcp = FastMCP("local-tooling")

add_tools(mcp)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mcp.run()
