from ckanext.fynd.tools import tool


@tool(
    name="organization_list",
    description="List all organisations on the portal. Organisations are the publishers/owners of datasets.",
    input_schema={
        "type": "object",
        "properties": {
            "all_fields": {"type": "boolean", "default": False, "description": "Return full org details (True) or just names (False)"},
            "sort": {"type": "string", "description": "Sort order (e.g. 'title asc')"},
        },
    },
    category="organisations",
    auth_action="fynd_organization_list",
)
def organization_list(backend, params, context):
    return backend.call_action("organization_list", params, context)


@tool(
    name="organization_show",
    description="Get details for a specific organisation, including its datasets.",
    input_schema={
        "type": "object",
        "properties": {"id": {"type": "string", "description": "Organisation ID or name"}},
        "required": ["id"],
    },
    category="organisations",
    auth_action="fynd_organization_show",
)
def organization_show(backend, params, context):
    return backend.call_action("organization_show", params, context)
