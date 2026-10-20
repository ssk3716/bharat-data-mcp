# API Notes — Bharat Data MCP

## 1. Overview

This document records the results of API tests performed on the Bharat Data MCP project. The tests cover resource listing, agricultural market price data, pagination, response structure, and observed data-transfer performance.

The API returned successful resource-list responses with version `2.2.0` and status `ok`.

## 2. API Response Summary

| Property | Observed Value |
|---|---|
| Response message | `Resource lists` |
| API version | `2.2.0` |
| Response status | `ok` |
| Total records (sample test) | `20` |
| Total records (full listing test) | `10580` |
| Sample page size | `3` |
| Starting offset | `0` |

The API response includes pagination metadata and an array of market records.

## 3. Response Structure

A typical successful response follows this structure:

```json
{
  "message": "Resource lists",
  "version": "2.2.0",
  "status": "ok",
  "total": 10580,
  "count": 3,
  "limit": "3",
  "offset": "0",
  "records": []
}
```

The empty `records` array above is illustrative of the response structure only; actual successful test responses contained three records.

### Response fields

| Field | Description |
|---|---|
| `message` | Describes the response |
| `version` | API version reported by the server |
| `status` | Response status |
| `total` | Total number of matching records reported |
| `count` | Number of records returned in the response |
| `limit` | Requested or reported page size |
| `offset` | Starting position for pagination |
| `records` | Array of agricultural market price records |

**Note:** `limit` and `offset` were returned as strings in the supplied examples, while `total` and `count` were numeric values.

## 4. Market Record Schema

Each record represents an agricultural commodity price entry for a market and arrival date.

| Field | Example | Description |
|---|---|---|
| `state` | `Maharashtra` | State where the market is located |
| `district` | `Pune` | District associated with the market |
| `market` | `Pune(Khadiki)` | Market name |
| `commodity` | `Onion` | Agricultural commodity |
| `variety` | `Local` | Commodity variety |
| `grade` | `Local` | Reported commodity grade |
| `arrival_date` | `20/10/2026` | Date associated with the market entry |
| `min_price` | `1000` | Reported minimum price |
| `max_price` | `2600` | Reported maximum price |
| `modal_price` | `1800` | Reported modal price |

The price units were not explicitly included in the supplied response excerpts. Confirm the source API's documentation before describing them as rupees per quintal or using them for unit-sensitive calculations.

## 5. Test Results

### Test 1 — Limited resource listing

**Observed result:** The API returned 20 total records, with three records in the response.

| Property | Value |
|---|---|
| Status | `ok` |
| Version | `2.2.0` |
| Total records | `20` |
| Count | `3` |
| Limit | `3` |
| Offset | `0` |

The response contained the following Maharashtra onion market entries:

| District | Market | Commodity | Variety | Grade | Arrival Date | Min Price | Max Price | Modal Price |
|---|---|---|---|---|---|---:|---:|---:|
| Nashik | Pimpalgaon Baswant(Saykheda) | Onion | Unhali | Local | 20/10/2026 | 1940 | 4253 | 3800 |
| Pune | Pune(Khadiki) | Onion | Local | Local | 20/10/2026 | 1000 | 2600 | 1800 |
| Nashik | APMC Chandwad | Onion | Unhali | Local | 20/10/2026 | 1110 | 4455 | 4000 |

These values are transcribed from the supplied API response. Trailing spaces in some market names have been omitted for readability.

### Test 2 — Resource listing across markets and commodities

**Observed result:** The API reported 10,580 total records and returned three records.

| Property | Value |
|---|---|
| Status | `ok` |
| Version | `2.2.0` |
| Total records | `10580` |
| Count | `3` |
| Limit | `3` |
| Offset | `0` |

Sample records:

| State | District | Market | Commodity | Variety | Grade | Arrival Date | Min Price | Max Price | Modal Price |
|---|---|---|---|---|---|---|---:|---:|---:|
| Tripura | Dhalai | Kulai APMC | Bottle gourd | Bottle Gourd | Grade B | 20/10/2026 | 2500 | 3000 | 2800 |
| Tripura | Dhalai | Kulai APMC | Green Chilli | Green Chilly | Grade B | 20/10/2026 | 24000 | 25000 | 24500 |
| Andhra Pradesh | Prakasam | Maddipadu APMC | Bajra(Pearl Millet/Cumbu) | Bold | FAQ | 20/10/2026 | 2900 | 2900 | 2900 |

This test demonstrates that the returned records include multiple states, districts, markets, commodities, varieties, and grades.

## 6. Pagination

The observed response contains the following pagination fields:

- `limit`: The number of records requested or returned per page.
- `offset`: The starting position of the page.
- `count`: The actual number of records in the current response.
- `total`: The total number of matching records reported by the API.

In the supplied tests, `limit` was `3`, `offset` was `0`, and `count` was `3`.

For the response reporting `total = 10580`, a complete traversal would require approximately 3,527 pages at a page size of three, assuming the total remains stable and every page can be retrieved successfully.

**Implementation note:** The actual endpoint path, HTTP method, and accepted query parameter names should be verified from the API implementation or official documentation before adding request examples.

## 7. Data Transfer and Performance Observations

The terminal output included the following transfer readings:

| Test | Download Size | Reported Average Speed | Elapsed Time |
|---|---:|---:|---:|
| Transfer 1 | 379.3 kB | 27,308 B/s | 14 seconds |
| Transfer 2 | 377.8 kB | 132.9 kB/s | 2 seconds |
| Transfer 3 | 138.8 kB | 13,350 B/s | 10 seconds |

These values are transcribed from the supplied terminal output. They are preliminary observations, not a controlled performance benchmark. The requests, response sizes, network conditions, and measurement methods may differ.

Additional terminal output included:

```text
10580 1000 1000 1000 Barasat APMC | Pune(Manjri)
375 375 1000
```

The meaning of these values is unclear from the available context. They should be mapped to their corresponding commands or test cases before being interpreted or used as evidence of API behavior.

## 8. Validation Notes

The supplied test results establish that:

- The API returned a successful status in the shown resource-list responses.
- The reported API version was `2.2.0`.
- Responses included pagination metadata and structured market records.
- The observed dataset included multiple states and agricultural commodities.
- Price records included minimum, maximum, and modal price fields.
- Arrival dates were represented as `DD/MM/YYYY` in the supplied examples.

Further validation is recommended for:

- HTTP status codes and error response formats.
- Invalid pagination values and out-of-range offsets.
- Filtering and sorting behavior, if supported.
- Missing, null, or malformed record fields.
- Price units and source-data freshness.
- Consistency of `total` and `count` across pages.
- Response-time measurements under repeatable test conditions.

## 9. Limitations

This document is based on the supplied terminal output and JSON response excerpts. It does not independently verify the API implementation, authentication requirements, endpoint URLs, filtering capabilities, or the semantics of unexplained terminal values.

All examples should be checked against the current API implementation before being treated as a formal API contract.

## 10. Conclusion

The tested resource-list API returned structured agricultural market price records and pagination metadata. The observed responses provide a useful baseline for documenting resource retrieval and planning additional tests for pagination, data validation, error handling, and performance.




## 11. API Endpoint and Request Configuration

### Resource details

| Property | Value |
|---|---|
| API provider | data.gov.in |
| Resource ID | `9ef84268-d588-465a-a308-a864a43d0070` |
| Response format | JSON |
| API key | Supplied through the `DATA_GOV_IN_API_KEY` environment variable |
| Example page size | 3 or 1000 records |
| Data domain | Agricultural market prices |

### Base endpoint

```text
https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070
```

The requests use the following query parameters:

| Parameter | Purpose | Example |
|---|---|---|
| `api-key` | Authenticates the API request | `$env:DATA_GOV_IN_API_KEY` |
| `format` | Specifies the response format | `json` |
| `limit` | Sets the maximum number of records requested | `3`, `1000` |
| `filters[arrival_date]` | Filters records by arrival date | `13/10/2026` |
| `filters[state]` | Filters records by state | `maharashtra` |
| `filters[commodity]` | Filters records by commodity | `onion` |

The filter parameter names and values shown above are taken from the tested commands.

## 12. API Test Cases

The following commands were executed in Windows PowerShell using `curl.exe`.

### Test 1 — Filter by arrival date

```powershell
curl.exe -g "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=$env:DATA_GOV_IN_API_KEY&format=json&limit=3&filters[arrival_date]=13/10/2026"
```

**Purpose:** Retrieve up to three records matching the arrival date `13/10/2026`.

**Parameters tested:**
- Response format: JSON
- Record limit: 3
- Arrival date: 13 October 2026

**Result:** The command was supplied, but its corresponding JSON response was not provided. The filtering result therefore remains unverified.

### Test 2 — Filter by state and commodity

```powershell
curl.exe -g "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=$env:DATA_GOV_IN_API_KEY&format=json&limit=3&filters[state]=maharashtra&filters[commodity]=onion"
```

**Purpose:** Retrieve up to three records matching Maharashtra and onion.

**Parameters tested:**
- State: `maharashtra`
- Commodity: `onion`
- Record limit: 3

This test checks the combined use of two filters in a single request. The matching response was not supplied, so the actual returned records and filter behavior have not been independently verified.

### Test 3 — Retrieve Maharashtra records

```powershell
curl.exe -g "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=$env:DATA_GOV_IN_API_KEY&format=json&limit=1000&filters[state]=Maharashtra"
```

**Purpose:** Request up to 1,000 records filtered by Maharashtra.

This request is intended to retrieve a larger sample of state-specific agricultural market records.

The requested limit is not necessarily the number of records returned. The actual count depends on the available matching records and the API response.

### Test 4 — Save the response and inspect pagination metadata

```powershell
curl.exe -g "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=$env:DATA_GOV_IN_API_KEY&format=json&limit=1000&filters[state]=Maharashtra" -o test4.json

python -c "import json; d=json.load(open('test4.json')); print(d['total'], d['count'], d['limit'])"
```

**Purpose:** Save the API response locally and inspect its pagination metadata.

The first command writes the response body to `test4.json`. The Python command parses that JSON file and prints:

| Field | Meaning |
|---|---|
| `total` | Total matching records reported by the API |
| `count` | Number of records contained in the response |
| `limit` | Limit value reported by the API |

The output values should be recorded alongside the test results when available.

**Important:** `total` may exceed `count`. A request with `limit=1000` does not automatically retrieve every matching record if the dataset contains more than 1,000 records.

## 13. Command-Line Implementation Notes

### PowerShell environment variable

The commands use:

```powershell
$env:DATA_GOV_IN_API_KEY
```

Set the environment variable in the current PowerShell session before running the requests:

```powershell
$env:DATA_GOV_IN_API_KEY = "YOUR_API_KEY"
```

Replace the placeholder with your actual API key. Do not commit the key to source control or include its value in documentation, logs, or screenshots.

### Why `curl.exe -g` is used

The `-g` option disables curl's URL globbing. It is useful when URLs contain square brackets, such as `filters[state]` and `filters[commodity]`, preventing curl from interpreting those characters as URL globbing syntax.

### JSON parsing

The Python command uses the standard `json` module to parse the downloaded response. It assumes that:
- `test4.json` contains valid JSON.
- The response is a JSON object.
- The keys `total`, `count`, and `limit` exist.

If the API returns an error response or malformed JSON, the command may fail. For more robust testing, validate the HTTP status and response structure before reading these fields.

## 14. Test Summary

| Test | Operation | Expected observation |
|---|---|---|
| 1 | Arrival-date filter | Up to three records for the requested date |
| 2 | State and commodity filters | Up to three matching onion records for Maharashtra |
| 3 | Maharashtra filter | Up to 1,000 matching records |
| 4 | Save and parse response | Total, returned count, and reported limit |

The earlier API readings showed successful JSON resource-list responses with version `2.2.0`, status `ok`, and a reported total of `10,580` records in one test. These observations should remain separate from the Maharashtra-specific tests unless the corresponding outputs confirm that they belong to the same request.

## 15. Further Verification

Before treating the test suite as complete, record the actual output of each command and verify:

1. Whether the arrival-date filter returns records for the requested date.
2. Whether combined state and commodity filters work as intended.
3. Whether the Maharashtra request returns the expected number of records.
4. Whether `total`, `count`, and `limit` are consistent with the downloaded JSON.
5. Whether the response contains an API error or rate-limit message.
6. Whether additional requests are needed to retrieve all matching records.

