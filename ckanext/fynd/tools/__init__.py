from ckanext.fynd.config import enabled_tool_categories

TOOLS = []


def tool(name, description, input_schema, category, auth_action):
    def decorator(fn):
        TOOLS.append({
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "category": category,
            "auth_action": auth_action,
            "handler": fn,
        })
        return fn
    return decorator


def get_enabled_tools():
    enabled = enabled_tool_categories()
    return [t for t in TOOLS if t["category"] in enabled]


def get_tools_for_wire():
    return [
        {"name": t["name"], "description": t["description"], "inputSchema": t["inputSchema"]}
        for t in get_enabled_tools()
    ]


def get_tool_by_name(name):
    for t in get_enabled_tools():
        if t["name"] == name:
            return t
    return None
