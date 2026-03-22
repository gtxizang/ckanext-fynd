from ckanext.fynd.tools import tool


@tool(
    name="tag_list",
    description="List all tags on the portal. Tags are keywords attached to datasets.",
    input_schema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Filter tags by prefix (e.g. 'ener' matches 'energy')"},
        },
    },
    category="tags",
    auth_action="fynd_tag_list",
)
def tag_list(backend, params, context):
    return backend.call_action("tag_list", params, context)
