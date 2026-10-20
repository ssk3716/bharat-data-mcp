# bharat-data-mcp

An MCP (Model Context Protocol) server that gives AI assistants access to
Indian open data from data.gov.in.

## Goal
Let an assistant answer questions like "What is the modal price of onion in
Pune district this week?" by calling well-described tools.

## Tech stack
- Python 3.11+, official `mcp` SDK (FastMCP)
- httpx (async HTTP), pydantic (validation)
- SQLite or diskcache for response caching
- pytest + pytest-asyncio + respx (mock HTTP)
- ruff, GitHub Actions CI, Docker

## Folder structure
src/bharat_data_mcp/
  server.py        # FastMCP app, tool registration
  client.py        # data.gov.in API client (retry, rate limit, cache)
  tools/
    mandi.py       # mandi price tools
    (more datasets later)
  models.py        # pydantic models
tests/
evals/
  questions.yaml   # 30-50 questions with expected tool + expected answer checks
  run_evals.py     # scores tool selection + answer correctness
README.md
CLAUDE.md
Dockerfile

## Tools (v1)
1. search_mandi_prices(state, district?, commodity?, date?) -> list of prices
2. get_price_trend(commodity, state, days=7) -> min/max/modal over time
3. compare_markets(commodity, state, markets[]) -> side-by-side prices
4. list_datasets(query) -> search available data.gov.in resources (v2)

## Non-functional requirements
- API key read from env var DATA_GOV_IN_API_KEY, never hardcoded
- Cache responses (TTL 1 hour), retry with backoff on 429/5xx
- Clear error messages the LLM can act on (e.g. "no data for that district,
  try these nearby ones")
- Every tool has a precise docstring (this is what the LLM reads)
- Tests for every tool; no real network calls in unit tests

## Milestones
1. Skeleton server + one working tool
2. Client with caching/retry + tests
3. Remaining tools
4. Eval suite + accuracy numbers in README
5. Docker, CI, README with demo GIF, publish to PyPI

## Out of scope (for now)
UPI, IRCTC, DigiLocker (need partner access), a web UI.
