from bharat_data_mcp.server import ping


def test_ping_returns_pong() -> None:
    assert ping() == "pong"
