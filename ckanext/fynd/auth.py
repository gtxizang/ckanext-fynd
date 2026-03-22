import ckan.plugins.toolkit as toolkit

_AUTH_MAP = {
    "fynd_dataset_search": "package_search",
    "fynd_dataset_show": "package_show",
    "fynd_dataset_list": "package_list",
    "fynd_datastore_search": "datastore_search",
    "fynd_datastore_fields": "datastore_search",
    "fynd_resource_show": "resource_show",
    "fynd_organization_list": "organization_list",
    "fynd_organization_show": "organization_show",
    "fynd_group_list": "group_list",
    "fynd_group_show": "group_show",
    "fynd_tag_list": "tag_list",
}


def _make_auth_function(ckan_action):
    @toolkit.auth_allow_anonymous_access
    def auth_function(context, data_dict):
        try:
            toolkit.check_access(ckan_action, context, data_dict)
            return {"success": True}
        except toolkit.NotAuthorized:
            return {"success": False, "msg": "Not authorized"}
    return auth_function


def get_auth_functions():
    return {name: _make_auth_function(action) for name, action in _AUTH_MAP.items()}
