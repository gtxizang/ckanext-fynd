from ckanext.fynd.tools import tool


@tool(
    name="resource_show",
    description="Get metadata for a specific resource (file/API) within a dataset. Returns URL, format, size, and metadata.",
    input_schema={
        "type": "object",
        "properties": {"id": {"type": "string", "description": "Resource ID (UUID)"}},
        "required": ["id"],
    },
    category="datasets",
    auth_action="fynd_resource_show",
)
def resource_show(backend, params, context):
    return backend.call_action("resource_show", params, context)
