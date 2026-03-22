# ckanext-fynd

MCP (Model Context Protocol) server for CKAN. Enables AI assistants to search
datasets, query DataStore, and explore portal metadata through natural language.

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

## Endpoints

- `POST /mcp` — MCP Streamable HTTP endpoint (JSON-RPC 2.0)
- `GET /.well-known/mcp.json` — MCP auto-discovery document

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

Integration tests (requires CKAN at localhost:5050 with fynd installed):
```bash
pytest -m integration -v
```

## License

AGPL-3.0
