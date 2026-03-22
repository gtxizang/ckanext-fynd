import ckan.plugins.toolkit as toolkit


def is_enabled():
    return toolkit.asbool(toolkit.config.get("ckanext.fynd.enabled", "true"))


def enabled_tool_categories():
    raw = toolkit.config.get(
        "ckanext.fynd.tools", "datasets datastore organisations groups tags"
    )
    return set(s.strip() for s in raw.split() if s.strip())


def datastore_max_rows():
    return int(toolkit.config.get("ckanext.fynd.datastore_max_rows", "100"))


def openapi_integration_enabled():
    return toolkit.asbool(
        toolkit.config.get("ckanext.fynd.openapi_integration", "false")
    )
