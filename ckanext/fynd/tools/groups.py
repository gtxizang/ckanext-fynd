from ckanext.fynd.tools import tool


@tool(
    name="group_list",
    description="List all groups (themes/topics) on the portal. Groups categorise datasets by subject area.",
    input_schema={
        "type": "object",
        "properties": {
            "all_fields": {"type": "boolean", "default": False, "description": "Return full group details (True) or just names (False)"},
        },
    },
    category="groups",
    auth_action="fynd_group_list",
)
def group_list(backend, params, context):
    return backend.call_action("group_list", params, context)


@tool(
    name="group_show",
    description="Get details for a specific group, including its datasets.",
    input_schema={
        "type": "object",
        "properties": {"id": {"type": "string", "description": "Group ID or name"}},
        "required": ["id"],
    },
    category="groups",
    auth_action="fynd_group_show",
)
def group_show(backend, params, context):
    return backend.call_action("group_show", params, context)
