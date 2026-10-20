
import os
from typing import Any

import httpx

RESOURCE_URL = (
    "https://api.data.gov.in/resource/"
    "9ef84268-d588-465a-a308-a864a43d0070"
)


class DataGovInError(Exception):
    """Raised when the data.gov.in API request fails."""


async def fetch_mandi_prices(
    *,
    state: str | None = None,
    commodity: str | None = None,
    arrival_date: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Fetch daily mandi prices from data.gov.in."""

    api_key = os.getenv("DATA_GOV_IN_API_KEY")
    if not api_key:
        raise DataGovInError(
            "DATA_GOV_IN_API_KEY environment variable is not configured."
        )

    if not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000.")

    params: dict[str, str | int] = {
        "api-key": api_key,
        "format": "json",
        "limit": limit,
    }

    filters = {
        "state": state,
        "commodity": commodity,
        "arrival_date": arrival_date,
    }

    for name, value in filters.items():
        if value and value.strip():
            params[f"filters[{name}]"] = value.strip()

    try:
        async with httpx.AsyncClient(timeout=45.0, headers={"User-Agent": "curl/8.21.0", "Connection": "close"}) as client:
            response = await client.get(RESOURCE_URL, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        raise DataGovInError(
            f"data.gov.in returned HTTP {exc.response.status_code}."
        ) from exc
    except httpx.RequestError as exc:
        raise DataGovInError(
            "Could not connect to data.gov.in."
        ) from exc
    except ValueError as exc:
        raise DataGovInError(
            "data.gov.in returned invalid JSON."
        ) from exc

    if not isinstance(data, dict):
        raise DataGovInError("Unexpected API response format.")

    if data.get("status") not in (None, "ok"):
        raise DataGovInError(
            f"data.gov.in API error: {data.get('message', 'Unknown error')}"
        )

    records = data.get("records", [])
    if not isinstance(records, list):
        raise DataGovInError("API response contains invalid records.")

    return data
