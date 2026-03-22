from ckanext.fynd.tools import tool


@tool(
    name="dataset_search",
    description="Search datasets by keyword, filter, or facet. Returns matching datasets with metadata.",
    input_schema={
        "type": "object",
        "properties": {
            "q": {"type": "string", "description": "Search query (e.g. 'energy consumption')"},
            "fq": {"type": "string", "description": "Filter query in Solr syntax (e.g. 'organization:svk')"},
            "rows": {"type": "integer", "default": 10, "description": "Number of results to return"},
            "start": {"type": "integer", "default": 0, "description": "Offset for pagination"},
            "sort": {"type": "string", "description": "Sort order (e.g. 'relevance asc', 'metadata_modified desc')"},
            "facet_field": {"type": "array", "items": {"type": "string"}, "description": "Fields to facet on (e.g. ['organization', 'tags'])"},
        },
    },
    category="datasets",
    auth_action="fynd_dataset_search",
)
def dataset_search(backend, params, context):
    return backend.call_action("package_search", params, context)


@tool(
    name="dataset_show",
    description="Get full metadata for a specific dataset by ID or name. Returns title, description, resources, tags, and all metadata fields.",
    input_schema={
        "type": "object",
        "properties": {"id": {"type": "string", "description": "Dataset ID (UUID) or name (slug)"}},
        "required": ["id"],
    },
    category="datasets",
    auth_action="fynd_dataset_show",
)
def dataset_show(backend, params, context):
    return backend.call_action("package_show", params, context)


@tool(
    name="dataset_list",
    description="List all dataset names/IDs on the portal. Use dataset_show to get details for a specific dataset.",
    input_schema={
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Maximum datasets to return"},
            "offset": {"type": "integer", "description": "Offset for pagination"},
        },
    },
    category="datasets",
    auth_action="fynd_dataset_list",
)
def dataset_list(backend, params, context):
    return backend.call_action("package_list", params, context)
