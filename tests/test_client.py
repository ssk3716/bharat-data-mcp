
import httpx
import pytest
import respx

from bharat_data_mcp.client import (
    RESOURCE_URL,
    DataGovInError,
    fetch_mandi_prices,
)


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATA_GOV_IN_API_KEY", "test-api-key")


@pytest.mark.asyncio
@respx.mock
async def test_fetch_mandi_prices_success() -> None:
    route = respx.get(RESOURCE_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "ok",
                "count": 1,
                "total": 1,
                "records": [
                    {
                        "state": "Maharashtra",
                        "district": "Nashik",
                        "market": "Example Market",
                        "commodity": "Onion",
                        "min_price": 1940,
                        "max_price": 4253,
                        "modal_price": 3800,
                    }
                ],
            },
        )
    )

    result = await fetch_mandi_prices(
        state="Maharashtra",
        commodity="onion",
        limit=3,
    )

    assert route.called
    assert result["status"] == "ok"
    assert result["count"] == 1
    assert result["records"][0]["commodity"] == "Onion"

    request_params = route.calls[0].request.url.params
    assert request_params["api-key"] == "test-api-key"
    assert request_params["format"] == "json"
    assert request_params["limit"] == "3"
    assert request_params["filters[state]"] == "Maharashtra"
    assert request_params["filters[commodity]"] == "onion"


@pytest.mark.asyncio
async def test_missing_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATA_GOV_IN_API_KEY", raising=False)

    with pytest.raises(DataGovInError, match="not configured"):
        await fetch_mandi_prices()


@pytest.mark.asyncio
@respx.mock
async def test_http_error() -> None:
    respx.get(RESOURCE_URL).mock(return_value=httpx.Response(403))

    with pytest.raises(DataGovInError, match="HTTP 403"):
        await fetch_mandi_prices()


@pytest.mark.asyncio
async def test_invalid_limit() -> None:
    with pytest.raises(ValueError, match="limit"):
        await fetch_mandi_prices(limit=0)
