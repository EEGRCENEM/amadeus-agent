import logging

import dotenv
from fastmcp import FastMCP

from agent.tools import add_tools


mcp = FastMCP("local-tooling")

add_tools(mcp)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dotenv.load_dotenv()

    mcp.run()
