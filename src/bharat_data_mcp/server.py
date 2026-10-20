
from typing import Any

from mcp.server.fastmcp import FastMCP

from bharat_data_mcp.client import (
    DataGovInError,
    fetch_mandi_prices,
)

mcp = FastMCP("bharat-data-mcp")


@mcp.tool()
def ping() -> str:
    """Check whether the Bharat Data MCP server is responding."""
    return "pong"


@mcp.tool()
async def get_mandi_prices(
    state: str | None = None,
    commodity: str | None = None,
    arrival_date: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Get daily agricultural mandi prices from data.gov.in.

    Optional filters:
    - state: State name, for example Maharashtra.
    - commodity: Commodity name, for example Onion.
    - arrival_date: Arrival date in the API's expected format.
    - limit: Maximum number of records to return, from 1 to 1000.
    """
    try:
        return await fetch_mandi_prices(
            state=state,
            commodity=commodity,
            arrival_date=arrival_date,
            limit=limit,
        )
    except (DataGovInError, ValueError) as exc:
        return {"error": str(exc)}


def main() -> None:
    """Run the MCP server using its default stdio transport."""
    mcp.run()


if __name__ == "__main__":
    main()
