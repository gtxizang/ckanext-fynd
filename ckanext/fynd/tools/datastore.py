from ckanext.fynd.config import datastore_max_rows
from ckanext.fynd.tools import tool


@tool(
    name="datastore_search",
    description="Search records in a DataStore resource. Returns rows matching the query with field values.",
    input_schema={
        "type": "object",
        "properties": {
            "resource_id": {"type": "string", "description": "Resource ID (UUID)"},
            "q": {"type": "string", "description": "Full-text search query"},
            "filters": {"type": "object", "description": "Field-value filters (e.g. {'country': 'Sweden'})"},
            "limit": {"type": "integer", "description": "Max rows to return"},
            "offset": {"type": "integer", "description": "Row offset for pagination"},
            "fields": {"type": "array", "items": {"type": "string"}, "description": "Fields to return (default: all)"},
            "sort": {"type": "string", "description": "Sort order (e.g. 'date desc')"},
        },
        "required": ["resource_id"],
    },
    category="datastore",
    auth_action="fynd_datastore_search",
)
def datastore_search(backend, params, context):
    params = dict(params)  # defensive copy
    max_rows = datastore_max_rows()
    if params.get("limit") is not None:
        params["limit"] = min(int(params["limit"]), max_rows)
    else:
        params["limit"] = max_rows
    return backend.call_action("datastore_search", params, context)


@tool(
    name="datastore_fields",
    description="Get field definitions (names, types) for a DataStore resource. Use this to understand the schema before querying.",
    input_schema={
        "type": "object",
        "properties": {"resource_id": {"type": "string", "description": "Resource ID (UUID)"}},
        "required": ["resource_id"],
    },
    category="datastore",
    auth_action="fynd_datastore_fields",
)
def datastore_fields(backend, params, context):
    result = backend.call_action("datastore_search", {"resource_id": params["resource_id"], "limit": 0}, context)
    return {"fields": result.get("fields", [])}
