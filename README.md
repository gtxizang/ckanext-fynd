# ckanext-fynd

MCP ([Model Context Protocol](https://modelcontextprotocol.io/)) server for CKAN.

## What is MCP?

MCP is an open standard that lets AI assistants — Claude, ChatGPT, GitHub Copilot, and others — connect to external data sources through a structured protocol. Instead of scraping websites or relying on stale training data, an MCP-enabled assistant can query live systems directly.

Think of it as a USB-C port for AI: one standard interface that any compliant client can plug into.

## What does this extension do?

ckanext-fynd adds an MCP endpoint to your CKAN portal at `/mcp`. Once installed, any MCP-compatible AI assistant can:

- **Search datasets** by keyword, filter, or facet
- **Query DataStore records** with field-level filtering and sorting
- **Browse organisations, groups, and tags** to understand portal structure
- **Inspect resource schemas** before querying

All through natural language. A user asks "what energy datasets do you have?" and the assistant calls `dataset_search` under the hood, returning real results from your portal.

## Why run MCP inside CKAN?

There are existing standalone MCP servers for CKAN ([ondata](https://github.com/ondata/ckan-mcp-server), [ondics](https://github.com/ondics/ckan-mcp-server)), but they sit outside CKAN and talk to it over HTTP. That means:

- No access to private datasets (they can only see public API responses)
- No CKAN auth integration (they can't respect your permission model)
- No extension interoperability (they can't call other extensions' actions)
- Another service to deploy and maintain

ckanext-fynd runs **inside** CKAN as a native extension. It calls `toolkit.get_action()` directly, respects `check_access()` for every tool call, and inherits your existing auth configuration. If a user has permission to see a dataset through the web UI, they can see it through MCP. If they don't, they can't. No separate auth layer, no API key management, no proxy.

## Quick Example

```bash
# Search datasets
curl -X POST http://your-ckan/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"dataset_search","arguments":{"q":"energy","rows":5}},"id":1}'

# Get DataStore field definitions
curl -X POST http://your-ckan/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"datastore_fields","arguments":{"resource_id":"<uuid>"}},"id":2}'
```

## Auto-Discovery

The extension serves a discovery document at `/.well-known/mcp.json`, following the [draft MCP discovery specification](https://github.com/modelcontextprotocol/specification/discussions/69). When MCP clients implement auto-discovery, they'll find your portal automatically.

## Requirements

- CKAN 2.10+
- Python 3.10+

## Installation

```bash
pip install -e .
```

Add `fynd` to `ckan.plugins` in your CKAN config:

```ini
ckan.plugins = ... fynd
```

## Configuration

```ini
# Enable/disable the MCP endpoint (default: true)
ckanext.fynd.enabled = true

# Tool categories to enable (default: all)
ckanext.fynd.tools = datasets datastore organisations groups tags

# System-wide rate limit, requests per minute (default: 60, 0 = unlimited)
ckanext.fynd.rate_limit = 60

# Max rows from DataStore queries (default: 100)
ckanext.fynd.datastore_max_rows = 100
```

## Available Tools

| Tool | Description |
|------|-------------|
| `dataset_search` | Search datasets by keyword, filter, or facet |
| `dataset_show` | Get full metadata for a specific dataset |
| `dataset_list` | List all dataset names/IDs |
| `datastore_search` | Query records in a DataStore resource |
| `datastore_fields` | Get field definitions for a DataStore resource |
| `resource_show` | Get metadata for a specific resource |
| `organization_list` | List all organisations |
| `organization_show` | Get organisation details |
| `group_list` | List all groups/themes |
| `group_show` | Get group details |
| `tag_list` | List all tags |

## Testing

Unit tests (no CKAN required):
```bash
pytest ckanext/fynd/tests/ --ignore=ckanext/fynd/tests/test_integration.py -v
```

Integration tests (requires a running CKAN instance with fynd installed):
```bash
pytest -m integration -v
```

## License

AGPL-3.0
