## Bharat Data MCP — Mandi Prices

A Python-based Model Context Protocol (MCP) server that lets AI assistants retrieve live agricultural mandi price data from India's data.gov.in API.

### Features

- Fetch mandi prices by state and commodity.
- Filter records by arrival date.
- Configure the maximum number of returned records.
- Integrate with MCP-compatible clients such as Claude Desktop.
- Run automated tests with pytest.

### Prerequisites

- Python 3.13 or a compatible Python version.
- [uv](https://docs.astral.sh/uv/)
- An API key from [data.gov.in](https://data.gov.in/).
- Claude Desktop or another compatible MCP client.

### Installation

Clone the repository and enter the project directory:

```powershell
git clone https://github.com/ssk3716/bharat-data-mcp
cd bharat-data-mcp
```

Install the project dependencies:

```powershell
uv sync
```

### Configure the API key

Create a local `.env` file in the project root:

```dotenv
DATA_GOV_IN_API_KEY=your_api_key_here
```

Replace the placeholder with your own API key. Never commit `.env` or publish your API key.

### Run the MCP server

Start the server using:

```powershell
uv run python -m bharat_data_mcp.server
```

The server uses the MCP standard input/output (stdio) transport by default, making it suitable for local MCP clients.

### Connect to Claude Desktop

Open Claude Desktop's configuration file and add the following under `mcpServers`:

```json
{
  "mcpServers": {
    "bharat-data-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\path\\to\\bharat-data-mcp",
        "--env-file",
        ".env",
        "python",
        "-m",
        "bharat_data_mcp.server"
      ]
    }
  }
}
```

Replace `C:\\path\\to\\bharat-data-mcp` with the absolute path to your local project directory. Preserve any other existing MCP server entries in the configuration.

Save the file and restart Claude Desktop.

### Available tools

| Tool | Description |
|---|---|
| `ping` | Checks whether the MCP server responds. |
| `get_mandi_prices` | Retrieves mandi price data with optional state, commodity, and arrival-date filters and a configurable result limit. |

### Example prompts

Try these prompts in Claude Desktop after connecting the server:

- "Get the latest 3 onion mandi prices for Maharashtra."
- "Show mandi prices for wheat in Punjab."
- "Get mandi prices for Maharashtra for a specified arrival date."

The returned data includes fields such as district, market, commodity, variety, arrival date, minimum price, maximum price, and modal price when provided by the API.

### Run tests

Run the automated test suite:

```powershell
uv run pytest
```

### Security

- Keep API keys in your local environment or `.env` file.
- Never commit `.env`, API keys, or credentials.
- Do not publish diagnostic output containing authenticated request URLs.

### Data source

Price records are retrieved from the [data.gov.in](https://data.gov.in/) agricultural mandi price API. Data availability and freshness depend on the source API.
