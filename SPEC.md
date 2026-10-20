# bharat-data-mcp

An MCP (Model Context Protocol) server that gives AI assistants access to
Indian open data from data.gov.in, starting with mandi (agricultural market)
prices.

> **Status:** Draft v2. Items marked **[VERIFY]** are assumptions about the
> upstream API that must be confirmed in Milestone 0 before implementation.

## 1. Goal

Let an assistant answer questions like "What is the modal price of onion in
Pune district today?" by calling well-described tools, and **never present
stale, missing, or mis-united data as if it were current and correct.**

### Success criteria
- >= 85% tool-selection accuracy and >= 80% final-answer correctness on the
  frozen-fixture eval suite (Section 9), reported per model in the README.
- 0 known cases of the key appearing in logs, errors, or test fixtures.
- Every response states its units and `data_as_of`.
- Zero stdout pollution in stdio mode (verified by a protocol test).

### Non-goals / out of scope (for now)
UPI, IRCTC, DigiLocker (need partner access), a web UI, price forecasting.

## 2. Milestone 0: API spike (hard gate)

Before writing any tool, hit the real API and write `docs/api-notes.md`
recording:
- Resource IDs, field names, and a sample record for the mandi dataset.
- Whether the resource is a **current daily snapshot or a queryable history**
  **[VERIFY]**. This decides whether `get_price_trend` is feasible.
- Date coverage, update frequency, and typical data lag **[VERIFY]**.
- Pagination: default page size, max `limit`, offset behavior **[VERIFY]**.
- Filter syntax (`filters[state]=...`), case sensitivity, exact vs. partial
  match **[VERIFY]**.
- Rate limits and what the public sample key allows **[VERIFY]**.
- Value quirks: numbers as strings, "NA", date format (`dd/mm/yyyy`),
  market/variety/grade naming.
- Licensing terms (GODL-India): attribution, caching, redistribution.

**Gate output:** a go/no-go decision per v1 tool and a choice of historical
data strategy (Section 7). The tool list in Section 5 is conditional on this.

## 3. Tech stack
- Python 3.11+, official `mcp` SDK (FastMCP)
- httpx (async HTTP), pydantic v2 (validation, structured output schemas)
- rapidfuzz (fuzzy entity matching)
- diskcache or SQLite for caching (decide in Milestone 0; see Section 8)
- pytest + pytest-asyncio + respx (mock HTTP)
- ruff, mypy (or pyright), GitHub Actions CI
- Distribution: PyPI + `uvx` (primary), Docker (secondary, see Section 4)

## 4. Transport and distribution

**Decision (default, revisit if requirements change):**
- **Primary: stdio**, run locally via `uvx bharat-data-mcp`. Each user supplies
  their own `DATA_GOV_IN_API_KEY`. No auth or shared-key concerns.
- **Optional: streamable HTTP** mode behind a flag (`--transport http`) for
  self-hosting. A public hosted instance is **out of scope** until auth, rate
  limiting, and key-sharing are designed.
- Docker image targets the HTTP mode; docs must not suggest Docker for stdio
  clients without the correct `docker run -i` invocation.

**Stdio rules:**
- Nothing may write to stdout except the MCP protocol. No `print()`.
- All logging goes to **stderr** (or a file). Enforced by a test that spawns
  the server and asserts stdout contains only valid JSON-RPC.

## 5. Folder structure

```
src/bharat_data_mcp/
  server.py          # FastMCP app, tool registration, transport selection
  client.py          # data.gov.in client (retry, rate limit, cache, redaction)
  cache.py           # cache abstraction (TTL, stale-if-error)
  entities.py        # state/district/market/commodity index + fuzzy matching + aliases
  aliases.yaml       # multilingual / alternate names (kanda -> Onion)
  models.py          # pydantic models (upstream rows + tool outputs)
  logging_setup.py   # stderr-only logging, key-redaction filter
  tools/
    mandi.py         # mandi price tools
    discovery.py     # list_* / lookup tools
    (more datasets later)
tests/
  unit/              # mocked HTTP (respx)
  contract/          # live-schema checks (scheduled CI only)
  fixtures/          # recorded API responses
evals/
  questions.yaml
  run_evals.py
  fixtures/          # frozen data the evals run against
docs/
  api-notes.md       # output of Milestone 0
  CHANGELOG.md
README.md
CLAUDE.md
Dockerfile
```

## 6. Tools

All tools: read-only, annotated `readOnlyHint=true`, `openWorldHint=true`,
`idempotentHint=true`, and return **structured output** (pydantic schema)
plus a short human-readable summary. Tool names are a public API (Section 13).

### 6.1 Core (v1)
1. `search_mandi_prices(state, district?, commodity?, market?, date?, limit=20)`
   returns per-market rows (never averaged).
2. `compare_markets(commodity, state, markets[], date?)` returns per-market
   rows side by side, ordered, with the latest `arrival_date` for each.
3. `get_price_trend(commodity, state, market?, days=7)` returns min/max/modal
   over time. **Conditional on the Milestone 0 gate**; see Section 7. If
   history is unavailable this tool is dropped or renamed (for example
   `get_latest_price_snapshot`) and must not promise a trend.

### 6.2 Discovery / entity resolution (v1, required)
4. `list_states()`
5. `list_districts(state)`
6. `list_markets(state, district?)`
7. `list_commodities(query?)`: returns canonical names, varieties, and grades.
8. `lookup_entity(text, kind?)`: fuzzy-resolves free text ("pune", "kanda",
   "Onion Red") to canonical values with confidence scores.

### 6.3 Later (v2)
9. `list_datasets(query)`: search available data.gov.in resources.

### 6.4 Entity resolution rules
- Every tool input for state/district/market/commodity is normalized
  (case, whitespace, punctuation) then matched against the canonical index
  built from the data (not hardcoded).
- Exact match: proceed. One high-confidence fuzzy match: proceed **and say
  so** in the response ("interpreted 'pune' as 'Pune'"). Otherwise: return an
  error with top-N "did you mean" suggestions (Section 10).
- **Variety/grade policy** (finalize in Milestone 0): default to returning
  each variety/grade as separate rows; allow an optional `variety` filter;
  never silently merge.
- **Language support:** `aliases.yaml` maps common Hindi/Marathi/other names
  and transliterations to canonical commodity names (for example `kanda`,
  `कांदा` -> Onion). Aliases are data, versioned, and covered by tests.
- Market names like "Pune" vs "Pune(Moshi)" are distinct markets; the
  resolver must surface both when ambiguous.

## 7. Historical data strategy (decide at the Milestone 0 gate)

| Option | When | Cost |
|---|---|---|
| A. Live API only | A history-capable resource exists | Low |
| B. Local daily snapshot ingester (SQLite) | Only current-day data exists | Medium: scheduler, backfill gaps, storage, licensing check |
| C. Drop trends from v1 | Neither is acceptable | None |

If B: ingester is a separate entrypoint (`bharat-data-ingest`), idempotent,
records `fetched_at`, tolerates missed days, and the trend tool reports
**coverage** ("5 of 7 days available"). Trends must never interpolate silently.

## 8. Non-functional requirements

### 8.1 Response contract
- **Units in field names and docstrings:** `min_price_inr_per_quintal`,
  `max_price_inr_per_quintal`, `modal_price_inr_per_quintal` **[VERIFY unit]**.
  Optionally also provide `*_inr_per_kg` as derived fields, clearly labelled.
- Each row includes `arrival_date` (ISO 8601), `market`, `district`, `state`,
  `commodity`, `variety`, `grade`.
- Each response includes top-level `data_as_of` (latest `arrival_date`
  returned), `requested_date`, `fetched_at`, `source` (attribution string),
  and `is_stale` / `staleness_note` when the requested date has no data
  ("no data for 2026-10-20; latest available is 2026-10-17").
- Modal prices are **never averaged** across markets. District/state roll-ups
  report per-market rows plus min/max across markets, labelled as such.
- Define "this week" / "today" precisely in docstrings (Asia/Kolkata timezone,
  last N calendar days ending at the latest available date).

### 8.2 Size budget
- Default `limit=20`, hard max `limit=100`.
- Responses over the limit are truncated with `"truncated": true,
  "rows_omitted": N` and a hint on how to narrow the query.
- Summary-first output; full rows only when requested or small.

### 8.3 Data quality
- Pydantic models coerce string numerics, treat "NA"/empty as `null`, and
  parse `dd/mm/yyyy` to ISO dates.
- Bad-row policy: **drop and count**. Response includes
  `rows_dropped_invalid: N`. Fail the call only if the entire payload is
  unparseable (upstream schema drift), with a distinct error code.
- Sanity checks: `min <= modal <= max`; violations flagged, not silently fixed.

### 8.4 Configuration and secrets
- `DATA_GOV_IN_API_KEY` read from env; never hardcoded, never committed.
- Clear error if missing or rejected (Section 10), with README setup steps
  for obtaining a key. If a public sample key is supported, document its
  limits **[VERIFY]**.
- The key is sent as a query parameter, so it can appear in URLs. Requirements:
  - A logging filter and exception wrapper redact the key everywhere
    (logs, tool errors, tracebacks, repr of request objects).
  - Test: induce failures and assert the key string never appears in output.
  - Fixtures recorded for tests are scrubbed; a pre-commit/CI secret scan runs.

### 8.5 Caching
- Default TTL 1 hour (configurable via env).
- Cache key includes resource ID and **all** filters, `limit`, `offset`.
- **Stale-if-error:** if the API fails after retries, serve the expired cache
  entry and mark the response `served_from_stale_cache: true` with its age.
- Never cache error responses or empty results caused by errors.
- Safe under concurrent processes (diskcache/SQLite WAL); cache location
  configurable (`BHARAT_MCP_CACHE_DIR`), with a documented default.
- Entity index (states/districts/markets/commodities) cached longer
  (for example 24 hours), refreshed lazily.

### 8.6 Retry and rate limiting
- Retry with exponential backoff + jitter on 429/5xx and network timeouts;
  honor `Retry-After`. Max attempts and overall deadline configurable.
- Client-side concurrency limit and request-rate limiter.
- Explicit per-request timeout; no unbounded waits.

### 8.7 Logging and observability
- Structured logs to stderr only, redacted.
- Counters (logged periodically and on shutdown): requests per tool, cache
  hit rate, upstream error rate by status, stale-cache serves, fuzzy-match
  rate, rows dropped.
- Optional `--debug` flag for verbose logging; still redacted.

### 8.8 Licensing and attribution
- Include data source attribution in every response and the README, per
  data.gov.in / GODL-India terms (confirmed in Milestone 0).
- Confirm that caching and any snapshot storage/redistribution comply.

## 9. Testing and evals

### 9.1 Unit tests (no real network)
- Every tool, every error path, entity resolution, alias mapping, coercion,
  truncation, staleness flagging, key redaction, stderr-only logging.
- HTTP mocked with respx using scrubbed recorded fixtures.

### 9.2 Contract tests
- Scheduled CI job (daily/weekly), **separate from PR CI**, hits the live API
  with a CI secret and asserts the schema, field names, and basic invariants.
  Failure opens an issue; it does not block PRs.

### 9.3 Evals
- `evals/questions.yaml`: 40-60 questions run against **frozen fixtures**
  injected via the client, so expected answers are stable.
- Scored separately:
  1. **Tool selection** (correct tool called)
  2. **Argument correctness** (state/commodity/date resolved properly)
  3. **Final-answer correctness** (rule-based checks, with an LLM judge only
     where needed)
- **Negative / edge cases (at least 25% of the set):** nonexistent district,
  misspelled commodity, alias input (`kanda`), no data for requested date,
  ambiguous scope ("onion price in Maharashtra"), market ambiguity
  (Pune vs Pune(Moshi)), invalid/missing key, unit confusion (per kg vs
  per quintal), request for a trend if unavailable.
- Run against a stated list of models; report per-model scores, date, and
  server version in the README.
- A tiny **live smoke test** (non-gating) verifies end-to-end connectivity.

## 10. Error design (LLM-actionable)

Errors are structured: `code`, `message`, `suggestions`, `retryable`.
Examples:
- `ENTITY_NOT_FOUND`: "No district 'Punee' in Maharashtra. Did you mean:
  Pune, Parbhani, Palghar?"
- `NO_DATA_FOR_DATE`: "No data for 2026-10-20. Latest available: 2026-10-17.
  Re-call with date=2026-10-17 or omit date."
- `AMBIGUOUS_ENTITY`: lists candidates and asks the caller to pick.
- `AUTH_MISSING` / `AUTH_INVALID`: tells the *user* how to set the key.
- `UPSTREAM_UNAVAILABLE`: retryable, notes stale cache if available.
- `UPSTREAM_SCHEMA_CHANGED`: not retryable, asks to file an issue.
- Suggestions come from fuzzy matching on the canonical index (and an
  adjacency dataset only if Milestone 0 finds one); the server does not
  invent "nearby" districts.

## 11. Documentation requirements
- **Tool docstrings** are the LLM's interface: precise purpose, parameter
  formats and examples, units, date semantics, what is *not* returned,
  and when to prefer another tool.
- **README:** install (`uvx`), key setup, client configs (Claude Desktop,
  Claude Code, others), example prompts, supported datasets, limitations
  (data lag, sparsity), eval results table, attribution, demo GIF.
- **CLAUDE.md** contents: project overview and architecture; commands
  (test, lint, type-check, run server, run evals); coding conventions
  (async, pydantic models for all I/O, no print, stderr logging only);
  rules (never log or commit the key, units in field names, never average
  modal prices, never edit fixtures by hand); how to add a new dataset/tool;
  how to refresh fixtures; definition of done.

## 12. Security checklist
- [ ] Key never in logs, errors, fixtures, or repo history (redaction + scan)
- [ ] Inputs validated and length-limited; no injection into upstream filters
- [ ] No arbitrary URL fetching from tool arguments
- [ ] Upstream response content treated as data, not instructions (strip or
      escape free-text fields that could carry prompt injection)
- [ ] Dependencies pinned/audited; Docker runs as non-root
- [ ] HTTP mode (if enabled) binds to localhost by default

## 13. Versioning and change policy
- Semantic versioning. Tool names, parameters, and output field names are a
  public API: renames or removals are breaking changes (major bump) with a
  deprecation period and entries in `CHANGELOG.md`.
- New optional parameters and new output fields are minor changes.
- Tool descriptions affect model behavior; changes to docstrings re-run the
  eval suite before release.

## 14. Milestones

0. **API spike:** `docs/api-notes.md`, go/no-go per tool, historical data
   strategy, licensing check. *(gate)*
1. **Skeleton:** FastMCP server (stdio), key handling, stderr logging with
   redaction, one working tool (`search_mandi_prices`) end to end.
2. **Client:** retry/backoff, rate limiting, caching with stale-if-error,
   pydantic coercion, unit tests, stdout-cleanliness test.
3. **Entity layer:** canonical index, fuzzy matching, aliases, discovery
   tools, structured errors.
4. **Remaining tools:** `compare_markets`, trend tool (per Section 7),
   truncation and staleness behavior.
5. **Evals:** fixtures, `questions.yaml`, scoring for the three metrics,
   per-model results in README; contract-test CI job.
6. **Ship:** Docker, CI (lint, type-check, tests, secret scan), README with
   demo GIF, CHANGELOG, PyPI release (`uvx` install verified from a clean
   machine).

## 15. Open questions (resolve in Milestone 0)
- Does a historical mandi resource exist, or do we need the ingester?
- What are the real pagination limits and key-tier rate limits?
- How are varieties and grades represented, and how should they be exposed?
- Is there any district adjacency data, or is fuzzy matching all we have?
- What are the attribution and caching terms under GODL-India?
- Which additional languages/aliases are worth shipping in v1?
